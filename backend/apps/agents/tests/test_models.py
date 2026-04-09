from django.test import TestCase

from apps.agents.models import AgentProvider, AgentAPIKey, AgentConfig
from apps.agents.tests.factories import AgentProviderFactory, AgentAPIKeyFactory, AgentConfigFactory


class AgentProviderModelTest(TestCase):
    def test_create_provider_saves_all_fields(self):
        # Arrange & Act
        provider = AgentProviderFactory(
            name="OpenAI",
            slug="openai",
            description="OpenAI GPT models",
            website_url="https://platform.openai.com",
        )
        # Assert
        db = AgentProvider.objects.get(pk=provider.pk)
        self.assertEqual(db.name, "OpenAI")
        self.assertEqual(db.slug, "openai")
        self.assertTrue(db.is_active)
        self.assertFalse(db.is_deleted)

    def test_provider_str_returns_name(self):
        provider = AgentProviderFactory(name="Anthropic")
        self.assertEqual(str(provider), "Anthropic")

    def test_provider_slug_is_unique(self):
        AgentProviderFactory(slug="openai")
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            AgentProviderFactory(slug="openai")

    def test_soft_delete_does_not_remove_from_db(self):
        provider = AgentProviderFactory()
        provider.soft_delete()
        self.assertTrue(AgentProvider.objects.filter(pk=provider.pk).exists())
        provider.refresh_from_db()
        self.assertTrue(provider.is_deleted)

    def test_restore_after_soft_delete(self):
        provider = AgentProviderFactory()
        provider.soft_delete()
        provider.restore()
        provider.refresh_from_db()
        self.assertFalse(provider.is_deleted)


class AgentAPIKeyModelTest(TestCase):
    def test_create_key_saves_all_fields(self):
        provider = AgentProviderFactory()
        key = AgentAPIKeyFactory(
            provider=provider,
            name="Prod Key",
            key_preview="sk-proj-Ab...****",
            priority=1,
        )
        db = AgentAPIKey.objects.get(pk=key.pk)
        self.assertEqual(db.name, "Prod Key")
        self.assertEqual(db.key_preview, "sk-proj-Ab...****")
        self.assertEqual(db.priority, 1)
        self.assertTrue(db.is_active)
        self.assertFalse(db.is_deleted)
        self.assertIsNone(db.expires_at)
        self.assertIsNone(db.last_used_at)

    def test_key_str_contains_provider_and_name(self):
        provider = AgentProviderFactory(slug="openai")
        key = AgentAPIKeyFactory(provider=provider, name="Main Key")
        self.assertIn("openai", str(key))
        self.assertIn("Main Key", str(key))

    def test_multiple_keys_per_provider(self):
        provider = AgentProviderFactory()
        AgentAPIKeyFactory(provider=provider, priority=1)
        AgentAPIKeyFactory(provider=provider, priority=2)
        self.assertEqual(AgentAPIKey.objects.filter(provider=provider).count(), 2)

    def test_encrypted_key_is_not_plain_text(self):
        key = AgentAPIKeyFactory()
        self.assertNotEqual(key.encrypted_key, "sk-proj-testkey-1234567890abcdefghij")
        # Fernet tokens start with 'gAAAAA'
        self.assertTrue(key.encrypted_key.startswith("gAAAAA"))


class AgentConfigModelTest(TestCase):
    def test_create_config_saves_all_fields(self):
        provider = AgentProviderFactory()
        config = AgentConfigFactory(
            provider=provider,
            name="Default GPT-4o",
            model_name="gpt-4o",
            config_json={"temperature": 0.7, "max_tokens": 2048},
            is_default=True,
        )
        db = AgentConfig.objects.get(pk=config.pk)
        self.assertEqual(db.model_name, "gpt-4o")
        self.assertTrue(db.is_default)
        self.assertEqual(db.config_json["temperature"], 0.7)

    def test_config_str_contains_provider_and_name(self):
        provider = AgentProviderFactory(slug="anthropic")
        config = AgentConfigFactory(provider=provider, name="Claude Fast")
        self.assertIn("anthropic", str(config))
        self.assertIn("Claude Fast", str(config))

    def test_multiple_configs_per_provider(self):
        provider = AgentProviderFactory()
        AgentConfigFactory(provider=provider, name="Config A")
        AgentConfigFactory(provider=provider, name="Config B")
        self.assertEqual(AgentConfig.objects.filter(provider=provider).count(), 2)
