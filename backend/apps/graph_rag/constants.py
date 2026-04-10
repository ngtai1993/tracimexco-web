# Default retrieval config for new RAG instances
DEFAULT_RETRIEVAL_CONFIG = {
    "search_strategy": "hybrid",  # hybrid | vector | graph | adaptive
    "top_k_vector": 10,
    "top_k_graph": 5,
    "top_k_final": 5,
    "similarity_threshold": 0.7,
    "graph_depth": 2,
    "community_level": 1,
    "reranking_enabled": True,
    "query_decomposition": True,
    "max_sub_queries": 3,
    "self_verification": False,
    "embedding_model": "text-embedding-3-small",
    "images_enabled": False,
    "image_top_k": 3,
    "image_similarity_threshold": 0.6,
}

# Default generation config for new RAG instances
DEFAULT_GENERATION_CONFIG = {
    "temperature": 0.7,
    "max_tokens": 2048,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "response_format": "markdown",
    "language": "vi",
    "tone": "professional",
    "include_sources": True,
    "max_context_tokens": 4096,
    "stream": True,
}

# Default knowledge base config
DEFAULT_KB_CONFIG = {
    "chunk_strategy": "recursive",
    "chunk_size": 512,
    "chunk_overlap": 50,
    "embedding_model": "text-embedding-3-small",
}

# Allowed file types
ALLOWED_DOCUMENT_TYPES = ["pdf", "docx", "txt", "csv", "md"]
ALLOWED_IMAGE_TYPES = ["jpg", "jpeg", "png", "webp", "gif"]
MAX_FILE_SIZE_MB = 50

# Purpose choices
PURPOSE_CHOICES = [
    ("customer_support", "Hỗ trợ khách hàng"),
    ("content_creation", "Tạo nội dung"),
    ("code_assistant", "Trợ lý code"),
    ("data_analysis", "Phân tích dữ liệu"),
    ("education", "Giáo dục & đào tạo"),
    ("internal_qa", "Q&A nội bộ"),
    ("general", "Đa mục đích"),
    ("custom", "Tùy chỉnh"),
]

# Document source types
SOURCE_TYPE_CHOICES = [
    ("file_upload", "File Upload"),
    ("image_upload", "Image Upload"),
    ("url", "URL Import"),
    ("text", "Plain Text"),
    ("api", "API Import"),
]

# Document processing statuses
PROCESSING_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("processing", "Processing"),
    ("chunking", "Chunking"),
    ("embedding", "Embedding"),
    ("extracting_entities", "Extracting Entities"),
    ("captioning", "Captioning Image"),
    ("completed", "Completed"),
    ("failed", "Failed"),
]

# Entity types
ENTITY_TYPE_CHOICES = [
    ("person", "Person"),
    ("organization", "Organization"),
    ("location", "Location"),
    ("concept", "Concept"),
    ("event", "Event"),
    ("product", "Product"),
    ("technology", "Technology"),
    ("document", "Document"),
    ("image", "Image"),
    ("other", "Other"),
]

# Skill types
SKILL_TYPE_CHOICES = [
    ("builtin", "Built-in"),
    ("api_call", "External API Call"),
    ("custom", "Custom Implementation"),
]

# Message roles
MESSAGE_ROLE_CHOICES = [
    ("user", "User"),
    ("assistant", "Assistant"),
    ("system", "System"),
]

# Access levels
ACCESS_LEVEL_CHOICES = [
    ("use", "Sử dụng (chat only)"),
    ("use_upload", "Sử dụng + Upload docs"),
    ("view_analytics", "Xem analytics"),
    ("full", "Full access (trừ config)"),
]

# Feedback choices
FEEDBACK_CHOICES = [
    ("thumbs_up", "👍"),
    ("thumbs_down", "👎"),
]

# Config types
CONFIG_TYPE_CHOICES = [
    ("retrieval", "Retrieval Config"),
    ("generation", "Generation Config"),
    ("system_prompt", "System Prompt"),
]

# Graph statuses
GRAPH_STATUS_CHOICES = [
    ("not_built", "Not Built"),
    ("building", "Building"),
    ("ready", "Ready"),
    ("failed", "Failed"),
    ("rebuilding", "Rebuilding"),
]

# Image detection keywords (used by query analyzer)
IMAGE_QUERY_KEYWORDS = [
    "hình", "ảnh", "image", "photo", "picture", "minh họa", "biểu đồ",
    "chart", "diagram", "sơ đồ", "logo", "icon", "screenshot",
    "chụp màn hình", "figure", "illustration", "show me", "cho xem",
    "trông như thế nào", "looks like", "hiển thị", "display",
]
