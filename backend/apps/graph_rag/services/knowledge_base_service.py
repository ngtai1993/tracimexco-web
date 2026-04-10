import logging
from django.db import transaction, models

from apps.graph_rag.models import KnowledgeBase, Document
from apps.graph_rag.constants import ALLOWED_DOCUMENT_TYPES, ALLOWED_IMAGE_TYPES, MAX_FILE_SIZE_MB
from apps.graph_rag.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """Business logic cho Knowledge Base và Document CRUD."""

    @staticmethod
    def create_kb(
        *,
        name: str,
        slug: str,
        description: str = "",
        chunk_strategy: str = "recursive",
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        embedding_model: str = "text-embedding-3-small",
        created_by=None,
    ) -> KnowledgeBase:
        return KnowledgeBase.objects.create(
            name=name,
            slug=slug,
            description=description,
            chunk_strategy=chunk_strategy,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            embedding_model=embedding_model,
            created_by=created_by,
        )

    @staticmethod
    def upload_document(
        *,
        knowledge_base_id,
        title: str,
        file,
        description: str = "",
        created_by=None,
    ) -> Document:
        """Upload file (document hoặc image) — detect type, tạo Document, dispatch processing."""
        extension = file.name.rsplit(".", 1)[-1].lower() if "." in file.name else ""
        file_size_mb = file.size / (1024 * 1024)

        if file_size_mb > MAX_FILE_SIZE_MB:
            raise DocumentProcessingError(
                f"File quá lớn ({file_size_mb:.1f}MB). Tối đa {MAX_FILE_SIZE_MB}MB."
            )

        is_image = extension in ALLOWED_IMAGE_TYPES
        is_document = extension in ALLOWED_DOCUMENT_TYPES

        if not is_image and not is_document:
            raise DocumentProcessingError(
                f"File type '{extension}' không được hỗ trợ. "
                f"Hỗ trợ: {', '.join(ALLOWED_DOCUMENT_TYPES + ALLOWED_IMAGE_TYPES)}"
            )

        source_type = "image_upload" if is_image else "file_upload"

        doc = Document.objects.create(
            knowledge_base_id=knowledge_base_id,
            title=title,
            description=description,
            source_type=source_type,
            file=file,
            is_image=is_image,
            processing_status="pending",
            metadata={
                "file_name": file.name,
                "file_size": file.size,
                "mime_type": getattr(file, "content_type", ""),
                "extension": extension,
            },
        )

        # Update KB stats
        kb = KnowledgeBase.objects.get(id=knowledge_base_id)
        if is_image:
            KnowledgeBase.objects.filter(id=knowledge_base_id).update(
                image_count=kb.image_count + 1
            )
        else:
            KnowledgeBase.objects.filter(id=knowledge_base_id).update(
                document_count=kb.document_count + 1
            )

        # Dispatch async processing
        try:
            from tasks.graph_rag_tasks import task_process_document
            task_process_document.delay(str(doc.id))
        except Exception:
            logger.warning("Celery unavailable, document %s queued as pending", doc.id)

        return doc

    @staticmethod
    def add_text_document(
        *,
        knowledge_base_id,
        title: str,
        content_text: str,
        description: str = "",
    ) -> Document:
        doc = Document.objects.create(
            knowledge_base_id=knowledge_base_id,
            title=title,
            description=description,
            source_type="text",
            content_text=content_text,
            processing_status="pending",
        )
        KnowledgeBase.objects.filter(id=knowledge_base_id).update(
            document_count=models.F("document_count") + 1
        )

        try:
            from tasks.graph_rag_tasks import task_process_document
            task_process_document.delay(str(doc.id))
        except Exception:
            logger.warning("Celery unavailable for doc %s", doc.id)

        return doc

    @staticmethod
    def add_url_document(
        *,
        knowledge_base_id,
        title: str,
        source_url: str,
        description: str = "",
    ) -> Document:
        doc = Document.objects.create(
            knowledge_base_id=knowledge_base_id,
            title=title,
            description=description,
            source_type="url",
            source_url=source_url,
            processing_status="pending",
        )
        KnowledgeBase.objects.filter(id=knowledge_base_id).update(
            document_count=models.F("document_count") + 1
        )

        try:
            from tasks.graph_rag_tasks import task_process_document
            task_process_document.delay(str(doc.id))
        except Exception:
            logger.warning("Celery unavailable for doc %s", doc.id)

        return doc

    @staticmethod
    def soft_delete_document(document_id) -> None:
        with transaction.atomic():
            doc = Document.objects.get(id=document_id, is_deleted=False)
            doc.soft_delete()
            # Update KB stats
            kb = doc.knowledge_base
            if doc.is_image:
                KnowledgeBase.objects.filter(id=kb.id).update(
                    image_count=max(0, kb.image_count - 1)
                )
            else:
                KnowledgeBase.objects.filter(id=kb.id).update(
                    document_count=max(0, kb.document_count - 1),
                    total_chunks=max(0, kb.total_chunks - doc.chunk_count),
                )

    @staticmethod
    def soft_delete_kb(kb_id) -> None:
        with transaction.atomic():
            KnowledgeBase.objects.filter(id=kb_id, is_deleted=False).update(
                is_deleted=True
            )
            Document.objects.filter(knowledge_base_id=kb_id).update(is_deleted=True)
