from unittest.mock import patch

from django.test import TestCase, override_settings

from apps.agents.exceptions import (
    AgentAPIKeyNotFound,
    AgentConfigNotFound,
    AgentDecryptionError,
    AgentProviderNotFound,
)
from apps.agents.models import AgentAPIKey, AgentConfig
from apps.agents.services.agent_encryption_service import AgentEncryptionService
from apps.agents.services.agent_key_service import AgentKeyService
from apps.agents.tests.factories import (
    TEST_FERNET_KEY,
    TEST_RAW_KEY,
    AgentAPIKeyFactory,
    AgentConfigFactory,
    AgentProviderFactory,
)


# ---------------------------------------------------------------------------
# AgentEncryptionService
# ---------------------------------------------------------------------------

@override_settings(AGENT_ENCRYPTION_KEY=TEST_FERNET_KEY)
class AgentEncryptionServiceTest(TestCase):
    def test_encrypt_returns_non_plain_text(self):
        result = AgentEncryptionService.encrypt("my-secret-key")
        self.assertNotEqual(result, "my-secret-key")
        self.assertTrue(result.startswith("gAAAAA"))

    def test_decrypt_returns_original_value(self):
        encrypted = AgentEncryptionService.encrypt(TEST_RAW_KEY)
        result = AgentEncryptionService.decrypt(encrypted)
        self.assertEqual(result, TEST_RAW_KEY)

    def test_decrypt_invalid_token_raises_decryption_error(self):
        with self.assertRaises(AgentDecryptionError):
            AgentEncryptionService.decrypt("not-a-valid-fernet-token")

    def test_generate_preview_shows_first_8_chars(self):
        preview = AgentEncryptionService.generate_preview("sk-proj-ABCDEFGHIJKLMNOP")
        self.assertTrue(preview.startswith("sk-proj-"))
        self.assertIn("...****", preview)

    def test_encrypt_then_decrypt_roundtrip(self):
        for raw in ["sk-test-1", "key-with-special-!@#", "a" * 100]:
            encrypted = AgentEncryptionService.encrypt(raw)
            self.assertEqual(AgentEncryptionService.decrypt(encrypted), raw)

    def test_missing_encryption_key_raises_error(self):
        with override_settings(AGENT_ENCRYPTION_KEY=""):
            with self.assertRaises(AgentDecryptionError):
                AgentEncryptionService.encrypt("any")


# ---------------------------------------------------------------------------
# AgentKeyService — get_active_key
# ---------------------------------------------------------------------------

@override_settings(AGENT_ENCRYPTION_KEY=TEST_FERNET_KEY)
class AgentKeyServiceGetActiveKeyTest(TestCase):
    def test_get_active_key_returns_decrypted_key(self):
        # Arrange
        provider = AgentProviderFactory(slug="openai")
        AgentAPIKeyFactory(provider=provider, priority=1)

        # Act — mock Celery task to avoid broker dependency
        with patch("tasks.agent_tasks.task_mark_key_used.delay"):
            result = AgentKeyService.get_active_key("openai")

        # Assert
        self.assertEqual(result, TEST_RAW_KEY)

    def test_get_active_key_respects_priority_order(self):
        # Arrange — key priority 2 and priority 1; should pick priority 1
        provider = AgentProviderFactory(slug="anthropic")
        from cryptography.fernet import Fernet
        f = Fernet(TEST_FERNET_KEY.encode())
        key_low = AgentAPIKeyFactory(
            provider=provider,
            priority=2,
            encrypted_key=f.encrypt(b"low-priority-key").decode(),
        )
        key_high = AgentAPIKeyFactory(
            provider=provider,
            priority=1,
            encrypted_key=f.encrypt(b"high-priority-key").decode(),
        )

        with patch("tasks.agent_tasks.task_mark_key_used.delay"):
            result = AgentKeyService.get_active_key("anthropic")

        self.assertEqual(result, "high-priority-key")

    def test_get_active_key_skips_inactive_keys(self):
        provider = AgentProviderFactory(slug="gemini")
        AgentAPIKeyFactory(provider=provider, is_active=False)

        with self.assertRaises(AgentAPIKeyNotFound):
            AgentKeyService.get_active_key("gemini")

    def test_get_active_key_provider_not_found_raises_error(self):
        with self.assertRaises(AgentProviderNotFound):
            AgentKeyService.get_active_key("nonexistent-provider")

    def test_get_active_key_inactive_provider_raises_error(self):
        AgentProviderFactory(slug="disabled", is_active=False)
        with self.assertRaises(AgentProviderNotFound):
            AgentKeyService.get_active_key("disabled")

    def test_get_active_key_no_keys_raises_error(self):
        AgentProviderFactory(slug="empty-provider")
        with self.assertRaises(AgentAPIKeyNotFound):
            AgentKeyService.get_active_key("empty-provider")

    def test_get_active_key_updates_last_used_via_fallback_when_celery_unavailable(self):
        provider = AgentProviderFactory(slug="cohere")
        key = AgentAPIKeyFactory(provider=provider)

        # Simulate Celery not available → fallback to direct DB write
        with patch("tasks.agent_tasks.task_mark_key_used.delay", side_effect=Exception("no broker")):
            AgentKeyService.get_active_key("cohere")

        key.refresh_from_db()
        self.assertIsNotNone(key.last_used_at)


# ---------------------------------------------------------------------------
# AgentKeyService — create_key / update_key / soft_delete_key
# ---------------------------------------------------------------------------

@override_settings(AGENT_ENCRYPTION_KEY=TEST_FERNET_KEY)
class AgentKeyServiceCRUDTest(TestCase):
    def test_create_key_stores_encrypted_not_plain(self):
        provider = AgentProviderFactory()
        key = AgentKeyService.create_key(
            provider_id=provider.id,
            name="Test Key",
            raw_key="sk-plaintext-raw-key",
            priority=1,
        )
        db = AgentAPIKey.objects.get(pk=key.pk)
        self.assertNotEqual(db.encrypted_key, "sk-plaintext-raw-key")
        self.assertTrue(db.encrypted_key.startswith("gAAAAA"))

    def test_create_key_preview_is_masked(self):
        provider = AgentProviderFactory()
        key = AgentKeyService.create_key(
            provider_id=provider.id,
            name="Key",
            raw_key="sk-proj-ABCDEFG",
        )
        self.assertIn("...****", key.key_preview)
        self.assertNotIn("ABCDEFG", key.key_preview)

    def test_create_key_records_created_by(self):
        from apps.agents.tests.factories import AdminUserFactory
        provider = AgentProviderFactory()
        user = AdminUserFactory()
        key = AgentKeyService.create_key(
            provider_id=provider.id,
            name="Key",
            raw_key=TEST_RAW_KEY,
            created_by=user,
        )
        self.assertEqual(key.created_by, user)

    def test_update_key_changes_allowed_fields(self):
        key = AgentAPIKeyFactory(name="Old Name", priority=1, is_active=True)
        updated = AgentKeyService.update_key(key.id, name="New Name", priority=3, is_active=False)
        self.assertEqual(updated.name, "New Name")
        self.assertEqual(updated.priority, 3)
        self.assertFalse(updated.is_active)

    def test_soft_delete_key_sets_is_deleted(self):
        key = AgentAPIKeyFactory()
        AgentKeyService.soft_delete_key(key.id)
        key.refresh_from_db()
        self.assertTrue(key.is_deleted)

    def test_mark_key_used_sets_last_used_at(self):
        key = AgentAPIKeyFactory()
        self.assertIsNone(key.last_used_at)
        AgentKeyService.mark_key_used(str(key.id))
        key.refresh_from_db()
        self.assertIsNotNone(key.last_used_at)


# ---------------------------------------------------------------------------
# AgentKeyService — configs
# ---------------------------------------------------------------------------

@override_settings(AGENT_ENCRYPTION_KEY=TEST_FERNET_KEY)
class AgentKeyServiceConfigTest(TestCase):
    def test_get_default_config_returns_merged_dict(self):
        provider = AgentProviderFactory(slug="openai")
        AgentConfigFactory(
            provider=provider,
            model_name="gpt-4o",
            config_json={"temperature": 0.7, "max_tokens": 2048},
            is_default=True,
        )
        result = AgentKeyService.get_default_config("openai")
        self.assertEqual(result["model_name"], "gpt-4o")
        self.assertEqual(result["temperature"], 0.7)
        self.assertEqual(result["max_tokens"], 2048)

    def test_get_config_by_name_returns_correct_config(self):
        provider = AgentProviderFactory(slug="anthropic")
        AgentConfigFactory(
            provider=provider,
            name="Fast Mode",
            model_name="claude-3-5-haiku",
            config_json={"temperature": 0.3},
            is_active=True,
        )
        result = AgentKeyService.get_config_by_name("anthropic", "Fast Mode")
        self.assertEqual(result["model_name"], "claude-3-5-haiku")
        self.assertEqual(result["temperature"], 0.3)

    def test_create_config_with_is_default_true_unsets_previous_default(self):
        provider = AgentProviderFactory()
        old_default = AgentConfigFactory(provider=provider, is_default=True)
        new_default = AgentKeyService.create_config(
            provider_id=provider.id,
            name="New Default",
            model_name="gpt-4o",
            config_json={},
            is_default=True,
        )
        old_default.refresh_from_db()
        self.assertFalse(old_default.is_default)
        self.assertTrue(new_default.is_default)

    def test_create_config_without_is_default_does_not_affect_existing_default(self):
        provider = AgentProviderFactory()
        old_default = AgentConfigFactory(provider=provider, is_default=True)
        AgentKeyService.create_config(
            provider_id=provider.id,
            name="Non-default",
            model_name="gpt-3.5-turbo",
            config_json={},
            is_default=False,
        )
        old_default.refresh_from_db()
        self.assertTrue(old_default.is_default)

    def test_soft_delete_config_sets_is_deleted(self):
        config = AgentConfigFactory()
        AgentKeyService.soft_delete_config(config.id)
        config.refresh_from_db()
        self.assertTrue(config.is_deleted)

    def test_update_config_sets_new_default_and_unsets_old(self):
        provider = AgentProviderFactory()
        old = AgentConfigFactory(provider=provider, is_default=True)
        new = AgentConfigFactory(provider=provider, is_default=False)
        AgentKeyService.update_config(new.id, is_default=True)
        old.refresh_from_db()
        new.refresh_from_db()
        self.assertFalse(old.is_default)
        self.assertTrue(new.is_default)


# ---------------------------------------------------------------------------
# AgentKeyService — soft_delete_provider (cascade)
# ---------------------------------------------------------------------------

@override_settings(AGENT_ENCRYPTION_KEY=TEST_FERNET_KEY)
class AgentKeyServiceSoftDeleteProviderTest(TestCase):
    def test_soft_delete_provider_cascades_to_keys_and_configs(self):
        provider = AgentProviderFactory(slug="to-delete")
        key = AgentAPIKeyFactory(provider=provider)
        config = AgentConfigFactory(provider=provider)

        AgentKeyService.soft_delete_provider("to-delete")

        provider.refresh_from_db()
        key.refresh_from_db()
        config.refresh_from_db()
        self.assertTrue(provider.is_deleted)
        self.assertTrue(key.is_deleted)
        self.assertTrue(config.is_deleted)

    def test_soft_delete_nonexistent_provider_raises_error(self):
        with self.assertRaises(AgentProviderNotFound):
            AgentKeyService.soft_delete_provider("does-not-exist")
