from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.agents.models import AgentAPIKey, AgentConfig, AgentProvider
from apps.agents.tests.factories import (
    TEST_FERNET_KEY,
    TEST_RAW_KEY,
    AdminUserFactory,
    AgentAPIKeyFactory,
    AgentConfigFactory,
    AgentProviderFactory,
    UserFactory,
)


def _admin_client():
    client = APIClient()
    user = AdminUserFactory()
    client.force_authenticate(user=user)
    return client


def _user_client():
    client = APIClient()
    user = UserFactory()
    client.force_authenticate(user=user)
    return client


# ---------------------------------------------------------------------------
# Provider endpoints
# ---------------------------------------------------------------------------

@override_settings(AGENT_ENCRYPTION_KEY=TEST_FERNET_KEY)
class ProviderListCreateViewTest(TestCase):
    def test_list_providers_returns_200_for_admin(self):
        AgentProviderFactory(slug="openai")
        AgentProviderFactory(slug="anthropic")
        client = _admin_client()
        resp = client.get("/api/v1/agents/providers/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["data"]), 2)

    def test_list_providers_returns_403_for_non_admin(self):
        client = _user_client()
        resp = client.get("/api/v1/agents/providers/")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_providers_returns_401_for_unauthenticated(self):
        resp = APIClient().get("/api/v1/agents/providers/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_provider_returns_201(self):
        client = _admin_client()
        resp = client.post("/api/v1/agents/providers/", {
            "name": "OpenAI",
            "slug": "openai",
            "description": "GPT models",
            "website_url": "https://platform.openai.com",
            "is_active": True,
        }, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["data"]["slug"], "openai")
        self.assertTrue(AgentProvider.objects.filter(slug="openai").exists())

    def test_create_provider_returns_400_for_duplicate_slug(self):
        AgentProviderFactory(slug="openai")
        client = _admin_client()
        resp = client.post("/api/v1/agents/providers/", {
            "name": "OpenAI Dup",
            "slug": "openai",
        }, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_provider_returns_400_for_missing_required_fields(self):
        client = _admin_client()
        resp = client.post("/api/v1/agents/providers/", {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


@override_settings(AGENT_ENCRYPTION_KEY=TEST_FERNET_KEY)
class ProviderDetailViewTest(TestCase):
    def test_get_provider_returns_200(self):
        AgentProviderFactory(slug="openai")
        client = _admin_client()
        resp = client.get("/api/v1/agents/providers/openai/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["data"]["slug"], "openai")

    def test_get_provider_returns_404_for_nonexistent(self):
        client = _admin_client()
        resp = client.get("/api/v1/agents/providers/no-such-slug/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_provider_updates_fields(self):
        AgentProviderFactory(slug="openai", name="Old Name")
        client = _admin_client()
        resp = client.patch("/api/v1/agents/providers/openai/", {"name": "New Name"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["data"]["name"], "New Name")

    def test_delete_provider_returns_204(self):
        AgentProviderFactory(slug="to-delete")
        client = _admin_client()
        resp = client.delete("/api/v1/agents/providers/to-delete/")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(AgentProvider.objects.filter(slug="to-delete", is_deleted=True).exists())

    def test_delete_provider_cascades_to_keys_and_configs(self):
        provider = AgentProviderFactory(slug="cascade-test")
        key = AgentAPIKeyFactory(provider=provider)
        config = AgentConfigFactory(provider=provider)
        client = _admin_client()
        client.delete("/api/v1/agents/providers/cascade-test/")
        key.refresh_from_db()
        config.refresh_from_db()
        self.assertTrue(key.is_deleted)
        self.assertTrue(config.is_deleted)


# ---------------------------------------------------------------------------
# API Key endpoints
# ---------------------------------------------------------------------------

@override_settings(AGENT_ENCRYPTION_KEY=TEST_FERNET_KEY)
class KeyListCreateViewTest(TestCase):
    def test_list_keys_returns_200_with_masked_preview(self):
        provider = AgentProviderFactory(slug="openai")
        AgentAPIKeyFactory(provider=provider)
        client = _admin_client()
        resp = client.get("/api/v1/agents/providers/openai/keys/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        key_data = resp.data["data"][0]
        # encrypted_key must NOT appear in response
        self.assertNotIn("encrypted_key", key_data)
        self.assertIn("key_preview", key_data)

    def test_list_keys_returns_404_for_unknown_provider(self):
        client = _admin_client()
        resp = client.get("/api/v1/agents/providers/ghost/keys/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_key_returns_201_and_does_not_expose_raw_key(self):
        AgentProviderFactory(slug="openai")
        client = _admin_client()
        resp = client.post("/api/v1/agents/providers/openai/keys/", {
            "name": "Prod Key",
            "raw_key": TEST_RAW_KEY,
            "priority": 1,
        }, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("raw_key", resp.data["data"])
        self.assertNotIn("encrypted_key", resp.data["data"])
        self.assertIn("key_preview", resp.data["data"])

    def test_create_key_stores_encrypted_in_db(self):
        AgentProviderFactory(slug="openai")
        client = _admin_client()
        client.post("/api/v1/agents/providers/openai/keys/", {
            "name": "Test",
            "raw_key": TEST_RAW_KEY,
        }, format="json")
        key = AgentAPIKey.objects.filter(provider__slug="openai").first()
        self.assertIsNotNone(key)
        self.assertNotEqual(key.encrypted_key, TEST_RAW_KEY)

    def test_create_key_returns_400_for_missing_raw_key(self):
        AgentProviderFactory(slug="openai")
        client = _admin_client()
        resp = client.post("/api/v1/agents/providers/openai/keys/", {"name": "X"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_keys_returns_403_for_non_admin(self):
        AgentProviderFactory(slug="openai")
        client = _user_client()
        resp = client.get("/api/v1/agents/providers/openai/keys/")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


@override_settings(AGENT_ENCRYPTION_KEY=TEST_FERNET_KEY)
class KeyDetailViewTest(TestCase):
    def test_patch_key_updates_metadata(self):
        provider = AgentProviderFactory(slug="openai")
        key = AgentAPIKeyFactory(provider=provider, name="Old", is_active=True, priority=1)
        client = _admin_client()
        resp = client.patch(
            f"/api/v1/agents/providers/openai/keys/{key.id}/",
            {"name": "New", "is_active": False, "priority": 5},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        key.refresh_from_db()
        self.assertEqual(key.name, "New")
        self.assertFalse(key.is_active)
        self.assertEqual(key.priority, 5)

    def test_patch_key_ignores_encrypted_key_field(self):
        provider = AgentProviderFactory(slug="openai")
        key = AgentAPIKeyFactory(provider=provider)
        original_encrypted = key.encrypted_key
        client = _admin_client()
        client.patch(
            f"/api/v1/agents/providers/openai/keys/{key.id}/",
            {"encrypted_key": "injected-value"},
            format="json",
        )
        key.refresh_from_db()
        # encrypted_key must remain unchanged
        self.assertEqual(key.encrypted_key, original_encrypted)

    def test_delete_key_returns_204(self):
        provider = AgentProviderFactory(slug="openai")
        key = AgentAPIKeyFactory(provider=provider)
        client = _admin_client()
        resp = client.delete(f"/api/v1/agents/providers/openai/keys/{key.id}/")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        key.refresh_from_db()
        self.assertTrue(key.is_deleted)

    def test_patch_key_returns_404_for_nonexistent(self):
        AgentProviderFactory(slug="openai")
        import uuid
        client = _admin_client()
        resp = client.patch(
            f"/api/v1/agents/providers/openai/keys/{uuid.uuid4()}/",
            {"name": "X"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


# ---------------------------------------------------------------------------
# Config endpoints
# ---------------------------------------------------------------------------

@override_settings(AGENT_ENCRYPTION_KEY=TEST_FERNET_KEY)
class ConfigListCreateViewTest(TestCase):
    def test_list_configs_returns_200(self):
        provider = AgentProviderFactory(slug="openai")
        AgentConfigFactory(provider=provider)
        client = _admin_client()
        resp = client.get("/api/v1/agents/providers/openai/configs/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["data"]), 1)

    def test_create_config_returns_201(self):
        AgentProviderFactory(slug="openai")
        client = _admin_client()
        resp = client.post("/api/v1/agents/providers/openai/configs/", {
            "name": "Default GPT-4o",
            "model_name": "gpt-4o",
            "config_json": {"temperature": 0.7, "max_tokens": 2048},
            "is_default": True,
        }, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["data"]["model_name"], "gpt-4o")
        self.assertTrue(resp.data["data"]["is_default"])

    def test_create_config_returns_400_for_missing_fields(self):
        AgentProviderFactory(slug="openai")
        client = _admin_client()
        resp = client.post("/api/v1/agents/providers/openai/configs/", {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_config_is_default_unsets_previous_default(self):
        provider = AgentProviderFactory(slug="openai")
        old_config = AgentConfigFactory(provider=provider, is_default=True)
        client = _admin_client()
        client.post("/api/v1/agents/providers/openai/configs/", {
            "name": "New Default",
            "model_name": "gpt-4o",
            "config_json": {},
            "is_default": True,
        }, format="json")
        old_config.refresh_from_db()
        self.assertFalse(old_config.is_default)


@override_settings(AGENT_ENCRYPTION_KEY=TEST_FERNET_KEY)
class ConfigDetailViewTest(TestCase):
    def test_patch_config_updates_fields(self):
        provider = AgentProviderFactory(slug="openai")
        config = AgentConfigFactory(provider=provider, name="Old", model_name="gpt-3.5-turbo")
        client = _admin_client()
        resp = client.patch(
            f"/api/v1/agents/providers/openai/configs/{config.id}/",
            {"model_name": "gpt-4o"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        config.refresh_from_db()
        self.assertEqual(config.model_name, "gpt-4o")

    def test_delete_config_returns_204(self):
        provider = AgentProviderFactory(slug="openai")
        config = AgentConfigFactory(provider=provider)
        client = _admin_client()
        resp = client.delete(f"/api/v1/agents/providers/openai/configs/{config.id}/")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        config.refresh_from_db()
        self.assertTrue(config.is_deleted)

    def test_delete_config_returns_404_for_nonexistent(self):
        AgentProviderFactory(slug="openai")
        import uuid
        client = _admin_client()
        resp = client.delete(f"/api/v1/agents/providers/openai/configs/{uuid.uuid4()}/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
