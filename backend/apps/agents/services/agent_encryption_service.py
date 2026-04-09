import logging
from django.conf import settings
from cryptography.fernet import Fernet, InvalidToken
from apps.agents.exceptions import AgentDecryptionError

logger = logging.getLogger(__name__)


def _get_fernet() -> Fernet:
    key = getattr(settings, "AGENT_ENCRYPTION_KEY", None)
    if not key:
        raise AgentDecryptionError("AGENT_ENCRYPTION_KEY chưa được cấu hình trong settings")
    raw = key.encode() if isinstance(key, str) else key
    return Fernet(raw)


class AgentEncryptionService:
    @staticmethod
    def encrypt(raw_key: str) -> str:
        f = _get_fernet()
        return f.encrypt(raw_key.encode()).decode()

    @staticmethod
    def decrypt(encrypted_key: str) -> str:
        f = _get_fernet()
        try:
            return f.decrypt(encrypted_key.encode()).decode()
        except InvalidToken as exc:
            raise AgentDecryptionError("Không thể giải mã API key — token không hợp lệ") from exc

    @staticmethod
    def generate_preview(raw_key: str) -> str:
        visible = raw_key[:8] if len(raw_key) >= 8 else raw_key
        return f"{visible}...****"
