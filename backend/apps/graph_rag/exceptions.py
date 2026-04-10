class RAGInstanceNotFound(Exception):
    """RAG instance không tồn tại hoặc không active."""
    pass


class KnowledgeBaseNotFound(Exception):
    """Knowledge Base không tồn tại."""
    pass


class DocumentNotFound(Exception):
    """Document không tồn tại."""
    pass


class KnowledgeGraphNotFound(Exception):
    """Knowledge Graph không tồn tại."""
    pass


class RAGSkillNotFound(Exception):
    """Skill không tồn tại."""
    pass


class RAGConversationNotFound(Exception):
    """Conversation không tồn tại."""
    pass


class RAGAccessDenied(Exception):
    """User không có quyền truy cập RAG instance."""
    pass


class RAGQuotaExceeded(Exception):
    """User đã vượt quá quota sử dụng."""
    pass


class DocumentProcessingError(Exception):
    """Lỗi khi xử lý document."""
    pass


class GraphBuildError(Exception):
    """Lỗi khi xây dựng Knowledge Graph."""
    pass


class ImageNotAllowed(Exception):
    """RAG instance không cho phép sử dụng hình ảnh."""
    pass
