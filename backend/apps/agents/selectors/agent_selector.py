from apps.agents.models import AgentProvider, AgentAPIKey, AgentConfig
from apps.agents.exceptions import (
    AgentProviderNotFound,
    AgentAPIKeyNotFound,
    AgentConfigNotFound,
)


class AgentSelector:
    @staticmethod
    def get_provider_by_slug(slug: str) -> AgentProvider:
        """Lấy provider active theo slug — dùng cho internal API."""
        try:
            return AgentProvider.objects.get(slug=slug, is_active=True, is_deleted=False)
        except AgentProvider.DoesNotExist:
            raise AgentProviderNotFound(f"Không tìm thấy provider với slug='{slug}'")

    @staticmethod
    def get_provider_by_slug_admin(slug: str) -> AgentProvider:
        """Lấy provider theo slug bất kể active hay không — dùng cho admin views."""
        try:
            return AgentProvider.objects.get(slug=slug, is_deleted=False)
        except AgentProvider.DoesNotExist:
            raise AgentProviderNotFound(f"Không tìm thấy provider với slug='{slug}'")

    @staticmethod
    def get_active_keys(provider_id):
        """Queryset keys active của provider, sắp xếp theo priority tăng dần (1 = ưu tiên nhất)."""
        return AgentAPIKey.objects.filter(
            provider_id=provider_id,
            is_active=True,
            is_deleted=False,
        ).order_by("priority")

    @staticmethod
    def get_default_config(provider_id) -> AgentConfig:
        try:
            return AgentConfig.objects.get(
                provider_id=provider_id,
                is_default=True,
                is_active=True,
                is_deleted=False,
            )
        except AgentConfig.DoesNotExist:
            raise AgentConfigNotFound(
                f"Không tìm thấy default config cho provider_id='{provider_id}'"
            )

    @staticmethod
    def get_config_by_name(provider_id, name: str) -> AgentConfig:
        try:
            return AgentConfig.objects.get(
                provider_id=provider_id,
                name=name,
                is_active=True,
                is_deleted=False,
            )
        except AgentConfig.DoesNotExist:
            raise AgentConfigNotFound(
                f"Không tìm thấy config '{name}' cho provider_id='{provider_id}'"
            )

    @staticmethod
    def list_providers(include_inactive: bool = False):
        qs = AgentProvider.objects.filter(is_deleted=False)
        if not include_inactive:
            qs = qs.filter(is_active=True)
        return qs

    @staticmethod
    def list_keys_for_provider(provider_id):
        return AgentAPIKey.objects.filter(
            provider_id=provider_id,
            is_deleted=False,
        ).order_by("priority")

    @staticmethod
    def list_configs_for_provider(provider_id):
        return AgentConfig.objects.filter(
            provider_id=provider_id,
            is_deleted=False,
        ).order_by("name")
