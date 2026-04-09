from django.test import TestCase

from apps.agents.exceptions import (
    AgentAPIKeyNotFound,
    AgentConfigNotFound,
    AgentProviderNotFound,
)
from apps.agents.selectors.agent_selector import AgentSelector
from apps.agents.tests.factories import (
    AgentAPIKeyFactory,
    AgentConfigFactory,
    AgentProviderFactory,
)


class AgentSelectorGetProviderTest(TestCase):
    def test_get_provider_by_slug_returns_active_provider(self):
        provider = AgentProviderFactory(slug="openai", is_active=True)
        result = AgentSelector.get_provider_by_slug("openai")
        self.assertEqual(result.pk, provider.pk)

    def test_get_provider_by_slug_raises_if_inactive(self):
        AgentProviderFactory(slug="inactive", is_active=False)
        with self.assertRaises(AgentProviderNotFound):
            AgentSelector.get_provider_by_slug("inactive")

    def test_get_provider_by_slug_raises_if_not_found(self):
        with self.assertRaises(AgentProviderNotFound):
            AgentSelector.get_provider_by_slug("no-such-provider")

    def test_get_provider_by_slug_raises_if_soft_deleted(self):
        provider = AgentProviderFactory(slug="deleted-one")
        provider.soft_delete()
        with self.assertRaises(AgentProviderNotFound):
            AgentSelector.get_provider_by_slug("deleted-one")

    def test_get_provider_by_slug_admin_returns_inactive_provider(self):
        provider = AgentProviderFactory(slug="paused", is_active=False)
        result = AgentSelector.get_provider_by_slug_admin("paused")
        self.assertEqual(result.pk, provider.pk)

    def test_get_provider_by_slug_admin_raises_if_soft_deleted(self):
        provider = AgentProviderFactory(slug="gone")
        provider.soft_delete()
        with self.assertRaises(AgentProviderNotFound):
            AgentSelector.get_provider_by_slug_admin("gone")


class AgentSelectorGetActiveKeysTest(TestCase):
    def test_get_active_keys_returns_only_active_non_deleted(self):
        provider = AgentProviderFactory()
        active = AgentAPIKeyFactory(provider=provider, is_active=True)
        AgentAPIKeyFactory(provider=provider, is_active=False)
        deleted = AgentAPIKeyFactory(provider=provider, is_active=True)
        deleted.soft_delete()

        qs = AgentSelector.get_active_keys(provider.id)
        pks = list(qs.values_list("pk", flat=True))
        self.assertIn(active.pk, pks)
        self.assertNotIn(deleted.pk, pks)
        self.assertEqual(len(pks), 1)

    def test_get_active_keys_ordered_by_priority(self):
        provider = AgentProviderFactory()
        key3 = AgentAPIKeyFactory(provider=provider, priority=3)
        key1 = AgentAPIKeyFactory(provider=provider, priority=1)
        key2 = AgentAPIKeyFactory(provider=provider, priority=2)

        keys = list(AgentSelector.get_active_keys(provider.id))
        priorities = [k.priority for k in keys]
        self.assertEqual(priorities, sorted(priorities))

    def test_get_active_keys_isolated_by_provider(self):
        provider_a = AgentProviderFactory()
        provider_b = AgentProviderFactory()
        AgentAPIKeyFactory(provider=provider_a)
        AgentAPIKeyFactory(provider=provider_b)

        keys_a = AgentSelector.get_active_keys(provider_a.id)
        for k in keys_a:
            self.assertEqual(k.provider_id, provider_a.id)


class AgentSelectorGetDefaultConfigTest(TestCase):
    def test_get_default_config_returns_is_default_true(self):
        provider = AgentProviderFactory()
        default_config = AgentConfigFactory(provider=provider, is_default=True, is_active=True)
        AgentConfigFactory(provider=provider, is_default=False, is_active=True)

        result = AgentSelector.get_default_config(provider.id)
        self.assertEqual(result.pk, default_config.pk)

    def test_get_default_config_raises_when_no_default(self):
        provider = AgentProviderFactory()
        AgentConfigFactory(provider=provider, is_default=False)
        with self.assertRaises(AgentConfigNotFound):
            AgentSelector.get_default_config(provider.id)

    def test_get_default_config_raises_when_default_is_inactive(self):
        provider = AgentProviderFactory()
        AgentConfigFactory(provider=provider, is_default=True, is_active=False)
        with self.assertRaises(AgentConfigNotFound):
            AgentSelector.get_default_config(provider.id)

    def test_get_default_config_isolated_per_provider(self):
        provider_a = AgentProviderFactory()
        provider_b = AgentProviderFactory()
        config_a = AgentConfigFactory(provider=provider_a, is_default=True, is_active=True)
        AgentConfigFactory(provider=provider_b, is_default=True, is_active=True)

        result = AgentSelector.get_default_config(provider_a.id)
        self.assertEqual(result.pk, config_a.pk)


class AgentSelectorListProvidersTest(TestCase):
    def test_list_providers_excludes_soft_deleted(self):
        active = AgentProviderFactory()
        deleted = AgentProviderFactory()
        deleted.soft_delete()

        qs = AgentSelector.list_providers()
        pks = list(qs.values_list("pk", flat=True))
        self.assertIn(active.pk, pks)
        self.assertNotIn(deleted.pk, pks)

    def test_list_providers_excludes_inactive_by_default(self):
        active = AgentProviderFactory(is_active=True)
        inactive = AgentProviderFactory(is_active=False)

        qs = AgentSelector.list_providers(include_inactive=False)
        pks = list(qs.values_list("pk", flat=True))
        self.assertIn(active.pk, pks)
        self.assertNotIn(inactive.pk, pks)

    def test_list_providers_includes_inactive_when_requested(self):
        inactive = AgentProviderFactory(is_active=False)
        qs = AgentSelector.list_providers(include_inactive=True)
        pks = list(qs.values_list("pk", flat=True))
        self.assertIn(inactive.pk, pks)
