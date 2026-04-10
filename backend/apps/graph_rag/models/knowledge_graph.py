from django.db import models
from common.models import BaseModel
from apps.graph_rag.constants import ENTITY_TYPE_CHOICES, GRAPH_STATUS_CHOICES


class KnowledgeGraph(BaseModel):
    """Metadata cho Knowledge Graph của một Knowledge Base."""

    knowledge_base = models.OneToOneField(
        "graph_rag.KnowledgeBase",
        on_delete=models.CASCADE,
        related_name="graph",
    )

    status = models.CharField(
        max_length=20, choices=GRAPH_STATUS_CHOICES, default="not_built"
    )

    # Stats
    entity_count = models.PositiveIntegerField(default=0)
    relationship_count = models.PositiveIntegerField(default=0)
    community_count = models.PositiveIntegerField(default=0)

    last_built_at = models.DateTimeField(null=True, blank=True)
    build_error = models.TextField(blank=True, default="")

    neo4j_graph_id = models.CharField(
        max_length=100, blank=True, default="",
        help_text="Identifier trong Neo4j để isolate data per KB",
    )

    class Meta:
        db_table = "rag_knowledge_graphs"

    def __str__(self):
        return f"Graph of {self.knowledge_base.name}"


class GraphEntity(BaseModel):
    """Một entity được extract từ documents."""

    knowledge_graph = models.ForeignKey(
        KnowledgeGraph, on_delete=models.CASCADE, related_name="entities"
    )

    name = models.CharField(max_length=500)
    entity_type = models.CharField(max_length=50, choices=ENTITY_TYPE_CHOICES)
    description = models.TextField(blank=True, default="")
    properties = models.JSONField(default=dict)

    source_chunks = models.ManyToManyField(
        "graph_rag.DocumentChunk", blank=True, related_name="entities"
    )

    neo4j_node_id = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        db_table = "rag_graph_entities"
        ordering = ["name"]
        unique_together = ["knowledge_graph", "name", "entity_type"]

    def __str__(self):
        return f"{self.name} ({self.entity_type})"


class GraphRelationship(BaseModel):
    """Quan hệ giữa hai entities."""

    knowledge_graph = models.ForeignKey(
        KnowledgeGraph, on_delete=models.CASCADE, related_name="relationships"
    )

    source_entity = models.ForeignKey(
        GraphEntity, on_delete=models.CASCADE, related_name="outgoing_relations"
    )
    target_entity = models.ForeignKey(
        GraphEntity, on_delete=models.CASCADE, related_name="incoming_relations"
    )

    relationship_type = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    weight = models.FloatField(default=1.0, help_text="Confidence score 0-1")
    properties = models.JSONField(default=dict)

    source_chunks = models.ManyToManyField(
        "graph_rag.DocumentChunk", blank=True, related_name="relationships"
    )

    neo4j_rel_id = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        db_table = "rag_graph_relationships"
        ordering = ["-weight"]

    def __str__(self):
        return f"{self.source_entity.name} —[{self.relationship_type}]→ {self.target_entity.name}"


class GraphCommunity(BaseModel):
    """Một community of related entities, với LLM-generated summary."""

    knowledge_graph = models.ForeignKey(
        KnowledgeGraph, on_delete=models.CASCADE, related_name="communities"
    )

    level = models.PositiveIntegerField(help_text="Hierarchy level (0 = most granular)")
    title = models.CharField(max_length=500)
    summary = models.TextField(help_text="LLM-generated summary of this community")
    rank = models.FloatField(default=0.0, help_text="Importance score")

    entities = models.ManyToManyField(
        GraphEntity, blank=True, related_name="communities"
    )

    class Meta:
        db_table = "rag_graph_communities"
        ordering = ["level", "-rank"]

    def __str__(self):
        return f"L{self.level}: {self.title}"
