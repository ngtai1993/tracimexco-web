class AgentProviderNotFound(Exception):
    """Provider không tồn tại hoặc không active."""
    pass


class AgentAPIKeyNotFound(Exception):
    """Không có API key nào active cho provider."""
    pass


class AgentConfigNotFound(Exception):
    """Không tìm thấy config cho provider."""
    pass


class AgentDecryptionError(Exception):
    """Lỗi giải mã API key."""
    pass
