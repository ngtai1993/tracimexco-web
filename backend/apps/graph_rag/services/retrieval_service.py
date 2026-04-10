import logging
import re

from django.db.models import Q

from apps.graph_rag.models import DocumentChunk, Document

logger = logging.getLogger(__name__)


class RetrievalService:
    """Multi-strategy retrieval engine with image support."""

    @staticmethod
    def _build_keyword_filter(query: str) -> Q:
        """Tạo OR-filter từ các từ khóa chính trong query (bỏ stop-words ngắn)."""
        stop = {"là", "và", "của", "trong", "the", "is", "a", "an", "to", "of", "in"}
        words = [
            w for w in re.split(r"[\s\.,;?!]+", query)
            if len(w) >= 3 and w.lower() not in stop
        ]
        if not words:
            words = [query[:50]]
        q = Q()
        for word in words[:8]:  # tối đa 8 từ khóa
            q |= Q(content__icontains=word)
        return q

    @staticmethod
    def vector_search(
        query: str, kb_ids: list[str], top_k: int = 10, threshold: float = 0.7
    ) -> list[dict]:
        """pgvector cosine similarity search. Fallback: keyword-based scoring until pgvector installed."""
        # Real implementation:
        # 1. Embed query using same embedding model
        # 2. SELECT * FROM rag_document_chunks ORDER BY embedding <=> query_embedding LIMIT top_k

        keyword_filter = RetrievalService._build_keyword_filter(query)
        chunks = DocumentChunk.objects.filter(
            document__knowledge_base_id__in=kb_ids,
            document__is_deleted=False,
            is_deleted=False,
            is_image_chunk=False,
        ).filter(keyword_filter)[:top_k]

        query_words = set(re.split(r"[\s\.,;?!]+", query.lower()))

        results = []
        for c in chunks.select_related("document"):
            chunk_lower = c.content.lower()
            overlap = sum(1 for w in query_words if len(w) >= 3 and w in chunk_lower)
            score = min(0.95, 0.4 + overlap * 0.1)
            results.append({
                "type": "chunk",
                "id": str(c.id),
                "content": c.content,
                "document_id": str(c.document_id),
                "document_title": c.document.title,
                "chunk_index": c.chunk_index,
                "score": round(score, 2),
                "metadata": c.metadata,
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    @staticmethod
    def image_search(
        query: str, kb_ids: list[str], top_k: int = 3, threshold: float = 0.6
    ) -> list[dict]:
        """Tìm images liên quan trong KB dựa trên caption similarity."""
        # Real implementation sẽ embed query → cosine search trên image chunks
        # Fallback: search trong image captions
        image_chunks = DocumentChunk.objects.filter(
            document__knowledge_base_id__in=kb_ids,
            document__is_deleted=False,
            is_deleted=False,
            is_image_chunk=True,
        ).select_related("document")

        results = []
        query_lower = query.lower()
        for chunk in image_chunks:
            # Simple relevance scoring based on keyword overlap
            caption = chunk.content.lower()
            words = query_lower.split()
            matches = sum(1 for w in words if w in caption)
            score = matches / max(len(words), 1)

            if score > 0.1:  # Minimum relevance
                results.append({
                    "type": "image",
                    "id": str(chunk.document.id),
                    "url": chunk.metadata.get("image_url", ""),
                    "caption": chunk.document.image_caption,
                    "title": chunk.document.title,
                    "tags": chunk.document.image_tags,
                    "score": score,
                    "metadata": chunk.metadata,
                })

        # Sort by score, return top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    @staticmethod
    def graph_search(
        query: str, kb_ids: list[str], depth: int = 2, top_k: int = 5
    ) -> list[dict]:
        """Neo4j graph traversal. Placeholder."""
        # Real implementation uses Neo4j Cypher queries
        return []

    @staticmethod
    def keyword_search(
        query: str, kb_ids: list[str], top_k: int = 10
    ) -> list[dict]:
        """Full-text search trên PostgreSQL."""
        keyword_filter = RetrievalService._build_keyword_filter(query)
        chunks = DocumentChunk.objects.filter(
            document__knowledge_base_id__in=kb_ids,
            document__is_deleted=False,
            is_deleted=False,
        ).filter(keyword_filter).select_related("document")[:top_k]

        return [
            {
                "type": "chunk",
                "id": str(c.id),
                "content": c.content,
                "document_id": str(c.document_id),
                "document_title": c.document.title,
                "score": 0.3,
                "metadata": c.metadata,
            }
            for c in chunks
        ]

    @staticmethod
    def hybrid_search(
        query: str,
        kb_ids: list[str],
        config: dict,
    ) -> dict:
        """
        Kết hợp tất cả strategies + image search nếu enabled.
        Returns: {"chunks": [...], "images": [...]}
        """
        top_k_vector = config.get("top_k_vector", 10)
        top_k_graph = config.get("top_k_graph", 5)
        top_k_final = config.get("top_k_final", 5)
        threshold = config.get("similarity_threshold", 0.7)
        images_enabled = config.get("images_enabled", False)
        image_top_k = config.get("image_top_k", 3)
        image_threshold = config.get("image_similarity_threshold", 0.6)

        # Text retrieval
        vector_results = RetrievalService.vector_search(
            query, kb_ids, top_k_vector, threshold
        )
        graph_results = RetrievalService.graph_search(
            query, kb_ids, config.get("graph_depth", 2), top_k_graph
        )

        # Merge + deduplicate text results
        seen = set()
        merged = []
        for result in vector_results + graph_results:
            rid = result["id"]
            if rid not in seen:
                seen.add(rid)
                merged.append(result)

        # Sort by score, take top_k_final
        merged.sort(key=lambda x: x.get("score", 0), reverse=True)
        chunks = merged[:top_k_final]

        # Image retrieval (only if enabled)
        images = []
        if images_enabled:
            needs_images = RetrievalService._query_needs_images(query)
            if needs_images:
                images = RetrievalService.image_search(
                    query, kb_ids, image_top_k, image_threshold
                )
                logger.info(
                    "Image search returned %d results for query: %s",
                    len(images), query[:80],
                )

        return {"chunks": chunks, "images": images}

    @staticmethod
    def _query_needs_images(query: str) -> bool:
        """Nhận diện xem query có cần hình ảnh không."""
        from apps.graph_rag.constants import IMAGE_QUERY_KEYWORDS

        query_lower = query.lower()
        for keyword in IMAGE_QUERY_KEYWORDS:
            if keyword in query_lower:
                return True

        # Nếu không match keywords, vẫn có thể cần ảnh
        # Real implementation: dùng LLM classifier
        return False
