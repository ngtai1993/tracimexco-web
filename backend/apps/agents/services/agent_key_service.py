import logging
from django.db import transaction
from django.utils import timezone

from apps.agents.models import AgentProvider, AgentAPIKey, AgentConfig
from apps.agents.selectors.agent_selector import AgentSelector
from apps.agents.services.agent_encryption_service import AgentEncryptionService
from apps.agents.exceptions import AgentAPIKeyNotFound

logger = logging.getLogger(__name__)


class AgentKeyService:
    @staticmethod
    def get_active_key(provider_slug: str) -> str:
        """Lấy plain text API key active có priority cao nhất của provider."""
        provider = AgentSelector.get_provider_by_slug(provider_slug)
        key = AgentSelector.get_active_keys(provider.id).first()
        if key is None:
            raise AgentAPIKeyNotFound(
                f"Không có API key nào active cho provider='{provider_slug}'"
            )
        plain_key = AgentEncryptionService.decrypt(key.encrypted_key)
        # Fire-and-forget: ghi last_used_at qua Celery để không block request
        try:
            from tasks.agent_tasks import task_mark_key_used
            task_mark_key_used.delay(str(key.id))
        except Exception:
            # Celery không khả dụng → ghi thẳng (fallback)
            AgentKeyService.mark_key_used(str(key.id))
        return plain_key

    @staticmethod
    def get_default_config(provider_slug: str) -> dict:
        """Lấy config mặc định của provider, trả về dict gồm model_name + config_json fields."""
        provider = AgentSelector.get_provider_by_slug(provider_slug)
        config = AgentSelector.get_default_config(provider.id)
        return {"model_name": config.model_name, **config.config_json}

    @staticmethod
    def get_config_by_name(provider_slug: str, name: str) -> dict:
        """Lấy config theo tên của provider."""
        provider = AgentSelector.get_provider_by_slug(provider_slug)
        config = AgentSelector.get_config_by_name(provider.id, name)
        return {"model_name": config.model_name, **config.config_json}

    @staticmethod
    def create_key(
        provider_id,
        name: str,
        raw_key: str,
        priority: int = 1,
        expires_at=None,
        created_by=None,
    ) -> AgentAPIKey:
        """Mã hóa raw_key rồi lưu vào DB. raw_key không được lưu."""
        encrypted = AgentEncryptionService.encrypt(raw_key)
        preview = AgentEncryptionService.generate_preview(raw_key)
        return AgentAPIKey.objects.create(
            provider_id=provider_id,
            name=name,
            encrypted_key=encrypted,
            key_preview=preview,
            priority=priority,
            expires_at=expires_at,
            created_by=created_by,
        )

    @staticmethod
    def update_key(key_id, **fields) -> AgentAPIKey:
        """Cập nhật metadata của key (name, priority, is_active, expires_at). Không cho sửa encrypted_key."""
        allowed = {"name", "priority", "is_active", "expires_at"}
        key = AgentAPIKey.objects.get(id=key_id, is_deleted=False)
        for field, value in fields.items():
            if field in allowed:
                setattr(key, field, value)
        key.save()
        return key

    @staticmethod
    def mark_key_used(key_id: str) -> None:
        AgentAPIKey.objects.filter(id=key_id).update(last_used_at=timezone.now())

    @staticmethod
    def soft_delete_key(key_id) -> None:
        AgentAPIKey.objects.filter(id=key_id, is_deleted=False).update(is_deleted=True)

    @staticmethod
    def create_config(
        provider_id,
        name: str,
        model_name: str,
        config_json: dict,
        is_default: bool = False,
        is_active: bool = True,
    ) -> AgentConfig:
        """Tạo config mới. Nếu is_default=True, tự động unset default cũ của cùng provider."""
        with transaction.atomic():
            if is_default:
                AgentConfig.objects.filter(
                    provider_id=provider_id,
                    is_default=True,
                    is_deleted=False,
                ).update(is_default=False)
            return AgentConfig.objects.create(
                provider_id=provider_id,
                name=name,
                model_name=model_name,
                config_json=config_json,
                is_default=is_default,
                is_active=is_active,
            )

    @staticmethod
    def update_config(config_id, **fields) -> AgentConfig:
        """Cập nhật config. Nếu is_default=True, unset default cũ của cùng provider."""
        allowed = {"name", "model_name", "config_json", "is_default", "is_active"}
        config = AgentConfig.objects.get(id=config_id, is_deleted=False)
        with transaction.atomic():
            if fields.get("is_default"):
                AgentConfig.objects.filter(
                    provider=config.provider,
                    is_default=True,
                    is_deleted=False,
                ).exclude(id=config_id).update(is_default=False)
            for field, value in fields.items():
                if field in allowed:
                    setattr(config, field, value)
            config.save()
        return config

    @staticmethod
    def soft_delete_config(config_id) -> None:
        AgentConfig.objects.filter(id=config_id, is_deleted=False).update(is_deleted=True)

    @staticmethod
    def soft_delete_provider(slug: str) -> None:
        """Soft delete provider và cascade toàn bộ keys + configs."""
        try:
            provider = AgentProvider.objects.get(slug=slug, is_deleted=False)
        except AgentProvider.DoesNotExist:
            from apps.agents.exceptions import AgentProviderNotFound
            raise AgentProviderNotFound(f"Không tìm thấy provider với slug='{slug}'")
        with transaction.atomic():
            provider.soft_delete()
            AgentAPIKey.objects.filter(provider=provider).update(is_deleted=True)
            AgentConfig.objects.filter(provider=provider).update(is_deleted=True)
