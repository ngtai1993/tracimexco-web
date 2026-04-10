import logging
from django.db import transaction
from django.utils import timezone

from apps.graph_rag.models import KnowledgeGraph, GraphEntity, GraphRelationship, GraphCommunity

logger = logging.getLogger(__name__)


class GraphBuilderService:
    """Xây dựng Knowledge Graph từ documents."""

    @staticmethod
    def build_graph(knowledge_base_id: str) -> None:
        """Build knowledge graph cho KB. Tạo entities, relationships, communities."""
        from apps.graph_rag.models import KnowledgeBase, DocumentChunk

        kb = KnowledgeBase.objects.get(id=knowledge_base_id, is_deleted=False)

        # Get or create graph
        graph, _ = KnowledgeGraph.objects.get_or_create(
            knowledge_base=kb,
            defaults={"neo4j_graph_id": str(kb.id)},
        )

        try:
            graph.status = "building"
            graph.save(update_fields=["status", "updated_at"])

            # Get all chunks (excluding image chunks for entity extraction)
            chunks = DocumentChunk.objects.filter(
                document__knowledge_base=kb,
                document__is_deleted=False,
                is_deleted=False,
            )

            # Extract entities
            entities_data = []
            for chunk in chunks.iterator():
                extracted = GraphBuilderService._extract_entities(chunk.content)
                for entity in extracted:
                    entity["chunk_id"] = str(chunk.id)
                entities_data.extend(extracted)

            # Deduplicate and create entities
            created_entities = GraphBuilderService._create_entities(graph, entities_data)

            # Extract relationships
            rels_data = GraphBuilderService._extract_relationships(
                chunks, created_entities
            )
            GraphBuilderService._create_relationships(graph, rels_data, created_entities)

            # Update graph stats
            graph.entity_count = GraphEntity.objects.filter(
                knowledge_graph=graph, is_deleted=False
            ).count()
            graph.relationship_count = GraphRelationship.objects.filter(
                knowledge_graph=graph, is_deleted=False
            ).count()
            graph.status = "ready"
            graph.last_built_at = timezone.now()
            graph.build_error = ""
            graph.save()

        except Exception as exc:
            logger.exception("Graph build failed for KB %s", knowledge_base_id)
            graph.status = "failed"
            graph.build_error = str(exc)
            graph.save(update_fields=["status", "build_error", "updated_at"])

    @staticmethod
    def rebuild_graph(knowledge_base_id: str) -> None:
        """Xóa graph cũ và build lại."""
        try:
            graph = KnowledgeGraph.objects.get(
                knowledge_base_id=knowledge_base_id, is_deleted=False
            )
            graph.status = "rebuilding"
            graph.save(update_fields=["status"])

            with transaction.atomic():
                GraphCommunity.objects.filter(knowledge_graph=graph).delete()
                GraphRelationship.objects.filter(knowledge_graph=graph).delete()
                GraphEntity.objects.filter(knowledge_graph=graph).delete()

        except KnowledgeGraph.DoesNotExist:
            pass

        GraphBuilderService.build_graph(knowledge_base_id)

    @staticmethod
    def _extract_entities(text: str) -> list[dict]:
        """Extract entities từ text. Placeholder — cần LLM."""
        # Real implementation sẽ dùng LLM:
        # prompt = "Extract named entities from this text..."
        # response = LLM call
        # return parsed entities
        return []

    @staticmethod
    def _create_entities(graph: KnowledgeGraph, entities_data: list[dict]) -> dict:
        """Deduplicate và tạo entities. Returns mapping name→entity."""
        created = {}
        for data in entities_data:
            key = (data.get("name", ""), data.get("type", "other"))
            if key not in created:
                entity, _ = GraphEntity.objects.get_or_create(
                    knowledge_graph=graph,
                    name=key[0],
                    entity_type=key[1],
                    defaults={
                        "description": data.get("description", ""),
                        "properties": data.get("properties", {}),
                    },
                )
                created[key] = entity
        return created

    @staticmethod
    def _extract_relationships(chunks, entities: dict) -> list[dict]:
        """Extract relationships. Placeholder — cần LLM."""
        return []

    @staticmethod
    def _create_relationships(
        graph: KnowledgeGraph, rels_data: list[dict], entities: dict
    ) -> None:
        for rel in rels_data:
            source_key = (rel.get("source"), rel.get("source_type"))
            target_key = (rel.get("target"), rel.get("target_type"))
            if source_key in entities and target_key in entities:
                GraphRelationship.objects.create(
                    knowledge_graph=graph,
                    source_entity=entities[source_key],
                    target_entity=entities[target_key],
                    relationship_type=rel.get("type", "related_to"),
                    description=rel.get("description", ""),
                    weight=rel.get("weight", 1.0),
                )
