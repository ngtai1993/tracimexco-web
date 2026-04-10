import logging
from django.utils import timezone

from apps.graph_rag.models import Document, DocumentChunk, KnowledgeBase

logger = logging.getLogger(__name__)


class DocumentProcessorService:
    """Pipeline xử lý document: parse → chunk → embed. Image: caption → embed."""

    @staticmethod
    def process_document(document_id: str) -> None:
        """Full processing pipeline cho 1 document hoặc image."""
        doc = Document.objects.select_related("knowledge_base").get(id=document_id)
        kb = doc.knowledge_base

        try:
            if doc.is_image:
                DocumentProcessorService._process_image(doc, kb)
            else:
                DocumentProcessorService._process_text_document(doc, kb)

            doc.processing_status = "completed"
            doc.processed_at = timezone.now()
            doc.save(update_fields=["processing_status", "processed_at", "updated_at"])

        except Exception as exc:
            logger.exception("Document processing failed for %s", document_id)
            doc.processing_status = "failed"
            doc.processing_error = str(exc)
            doc.save(
                update_fields=["processing_status", "processing_error", "updated_at"]
            )

    @staticmethod
    def _process_text_document(doc: Document, kb: KnowledgeBase) -> None:
        """Parse text → chunk → create DocumentChunks."""
        doc.processing_status = "processing"
        doc.save(update_fields=["processing_status"])

        # 1. Extract text if needed
        text = doc.content_text
        if not text and doc.file:
            text = DocumentProcessorService._extract_text_from_file(doc)
            doc.content_text = text
            doc.save(update_fields=["content_text"])

        if not text:
            raise ValueError("No text content to process")

        # 2. Chunk
        doc.processing_status = "chunking"
        doc.save(update_fields=["processing_status"])
        chunks = DocumentProcessorService._chunk_text(
            text=text,
            strategy=kb.chunk_strategy,
            chunk_size=kb.chunk_size,
            overlap=kb.chunk_overlap,
        )

        # 3. Create chunk records
        doc.processing_status = "embedding"
        doc.save(update_fields=["processing_status"])

        chunk_objects = []
        for i, chunk_text in enumerate(chunks):
            chunk_objects.append(
                DocumentChunk(
                    document=doc,
                    content=chunk_text,
                    chunk_index=i,
                    token_count=len(chunk_text.split()),
                    is_image_chunk=False,
                    metadata={"source": "text_document"},
                )
            )
        DocumentChunk.objects.bulk_create(chunk_objects)

        # 4. Update stats
        doc.chunk_count = len(chunks)
        doc.token_count = sum(c.token_count for c in chunk_objects)
        doc.save(update_fields=["chunk_count", "token_count"])

        KnowledgeBase.objects.filter(id=kb.id).update(
            total_chunks=kb.total_chunks + len(chunks)
        )

    @staticmethod
    def _process_image(doc: Document, kb: KnowledgeBase) -> None:
        """Generate caption cho image → create image chunk for vector search."""
        doc.processing_status = "captioning"
        doc.save(update_fields=["processing_status"])

        # Generate caption via LLM (multimodal)
        caption = DocumentProcessorService._generate_image_caption(doc)
        tags = DocumentProcessorService._extract_image_tags(caption)

        doc.image_caption = caption
        doc.image_tags = tags
        doc.content_text = caption  # Store caption as searchable text
        doc.save(update_fields=["image_caption", "image_tags", "content_text"])

        # Create a single chunk for the image caption (for vector search)
        doc.processing_status = "embedding"
        doc.save(update_fields=["processing_status"])

        image_url = doc.file.url if doc.file else ""
        DocumentChunk.objects.create(
            document=doc,
            content=f"[Image: {doc.title}] {caption}",
            chunk_index=0,
            token_count=len(caption.split()),
            is_image_chunk=True,
            metadata={
                "source": "image_caption",
                "image_url": image_url,
                "image_tags": tags,
                "original_title": doc.title,
            },
        )

        doc.chunk_count = 1
        doc.token_count = len(caption.split())
        doc.save(update_fields=["chunk_count", "token_count"])

        KnowledgeBase.objects.filter(id=kb.id).update(
            total_chunks=kb.total_chunks + 1
        )

    @staticmethod
    def _extract_text_from_file(doc: Document) -> str:
        """Extract text từ PDF, DOCX, TXT, etc. Placeholder — cần unstructured library."""
        ext = doc.file_extension

        if ext == "txt" or ext == "md":
            return doc.file.read().decode("utf-8", errors="replace")

        if ext == "csv":
            return doc.file.read().decode("utf-8", errors="replace")

        # PDF, DOCX: requires unstructured library
        # Placeholder implementation
        logger.info(
            "File extraction for '%s' requires unstructured library. "
            "Returning empty — install with: pip install unstructured[pdf,docx]",
            ext,
        )
        return ""

    @staticmethod
    def _chunk_text(
        text: str, strategy: str, chunk_size: int, overlap: int
    ) -> list[str]:
        """Chunk text theo strategy. Placeholder — cần langchain."""
        if not text.strip():
            return []

        # Simple fixed-size chunking (works without langchain)
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk.strip())
            start = end - overlap if overlap < chunk_size else end

        return chunks

    @staticmethod
    def _generate_image_caption(doc: Document) -> str:
        """Generate caption cho image via multimodal LLM. Placeholder."""
        # Real implementation sẽ:
        # 1. Load image file
        # 2. Call OpenAI GPT-4o / Anthropic Claude with image
        # 3. Return generated caption
        #
        # Example with OpenAI:
        # from apps.agents.services.agent_key_service import AgentKeyService
        # api_key = AgentKeyService.get_active_key("openai")
        # client = OpenAI(api_key=api_key)
        # response = client.chat.completions.create(
        #     model="gpt-4o",
        #     messages=[{
        #         "role": "user",
        #         "content": [
        #             {"type": "text", "text": "Mô tả chi tiết nội dung hình ảnh này..."},
        #             {"type": "image_url", "image_url": {"url": image_data_url}},
        #         ]
        #     }]
        # )
        # return response.choices[0].message.content

        title = doc.title or "Unknown image"
        return f"Hình ảnh: {title}. (Caption sẽ được tạo tự động khi kết nối LLM multimodal)"

    @staticmethod
    def _extract_image_tags(caption: str) -> list[str]:
        """Extract tags từ caption. Placeholder — cần LLM."""
        # Real implementation: LLM extract keywords/tags từ caption
        # Placeholder: simple keyword extraction
        tags = []
        keywords = ["product", "diagram", "chart", "screenshot", "photo", "logo", "icon"]
        caption_lower = caption.lower()
        for kw in keywords:
            if kw in caption_lower:
                tags.append(kw)
        return tags
