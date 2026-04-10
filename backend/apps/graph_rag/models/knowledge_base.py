from django.db import models
from common.models import BaseModel
from apps.graph_rag.constants import (
    SOURCE_TYPE_CHOICES,
    PROCESSING_STATUS_CHOICES,
    ALLOWED_IMAGE_TYPES,
)


CHUNK_STRATEGY_CHOICES = [
    ("fixed", "Fixed Size"),
    ("recursive", "Recursive Character"),
    ("semantic", "Semantic Chunking"),
]


class KnowledgeBase(BaseModel):
    """Bộ tài liệu nguồn cho RAG."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, default="")

    # Chunking configuration
    chunk_strategy = models.CharField(
        max_length=20, choices=CHUNK_STRATEGY_CHOICES, default="recursive"
    )
    chunk_size = models.PositiveIntegerField(default=512)
    chunk_overlap = models.PositiveIntegerField(default=50)

    # Embedding
    embedding_model = models.CharField(max_length=100, default="text-embedding-3-small")
    embedding_dimensions = models.PositiveIntegerField(default=1536)

    # Stats (denormalized)
    document_count = models.PositiveIntegerField(default=0)
    image_count = models.PositiveIntegerField(default=0)
    total_chunks = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, related_name="+"
    )

    class Meta:
        db_table = "rag_knowledge_bases"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Document(BaseModel):
    """Một tài liệu hoặc hình ảnh trong Knowledge Base."""

    knowledge_base = models.ForeignKey(
        KnowledgeBase, on_delete=models.CASCADE, related_name="documents"
    )

    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, default="")

    # Source
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES)
    source_url = models.URLField(blank=True, default="")
    file = models.FileField(upload_to="graph_rag/documents/", blank=True)
    content_text = models.TextField(blank=True, default="", help_text="Extracted raw text")

    # Image-specific fields
    is_image = models.BooleanField(default=False, db_index=True)
    image_caption = models.TextField(
        blank=True, default="",
        help_text="LLM-generated caption mô tả nội dung ảnh",
    )
    image_tags = models.JSONField(
        default=list,
        help_text="Auto-extracted tags: ['product', 'diagram', 'screenshot']",
    )

    # Processing status
    processing_status = models.CharField(
        max_length=30, choices=PROCESSING_STATUS_CHOICES, default="pending"
    )
    processing_error = models.TextField(blank=True, default="")
    processed_at = models.DateTimeField(null=True, blank=True)

    # Stats
    chunk_count = models.PositiveIntegerField(default=0)
    entity_count = models.PositiveIntegerField(default=0)
    token_count = models.PositiveIntegerField(default=0)

    # Metadata
    metadata = models.JSONField(
        default=dict,
        help_text="File size, page count, dimensions, mime_type, etc.",
    )

    class Meta:
        db_table = "rag_documents"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def file_extension(self) -> str:
        if self.file:
            return self.file.name.rsplit(".", 1)[-1].lower()
        return ""

    @property
    def is_image_file(self) -> bool:
        return self.file_extension in ALLOWED_IMAGE_TYPES


class DocumentChunk(BaseModel):
    """Một chunk của document hoặc caption của image, đã được embed."""

    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="chunks"
    )

    content = models.TextField()
    chunk_index = models.PositiveIntegerField()

    # Vector embedding sẽ được thêm khi cài pgvector extension
    # embedding = VectorField(dimensions=1536)

    # Metadata
    metadata = models.JSONField(
        default=dict,
        help_text="page_number, start_char, end_char, image_url, etc.",
    )
    token_count = models.PositiveIntegerField(default=0)

    # Đánh dấu chunk từ image caption (để image retrieval)
    is_image_chunk = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = "rag_document_chunks"
        ordering = ["document", "chunk_index"]

    def __str__(self):
        return f"Chunk #{self.chunk_index} of {self.document.title}"
