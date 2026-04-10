from unittest.mock import patch, MagicMock

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.graph_rag.models import RAGInstance, RAGAccessPermission
from apps.graph_rag.tests.factories import (
    RAGInstanceFactory,
    KnowledgeBaseFactory,
    DocumentFactory,
    DocumentChunkFactory,
    RAGSkillFactory,
    RAGConversationFactory,
    RAGMessageFactory,
    RAGAccessPermissionFactory,
    UserFactory,
    AdminUserFactory,
    RAGUsageLogFactory,
    RAGConfigHistoryFactory,
)

BASE_URL = "/api/v1/rag"


def _admin_client():
    client = APIClient()
    user = AdminUserFactory()
    client.force_authenticate(user=user)
    return client, user


def _user_client():
    client = APIClient()
    user = UserFactory()
    client.force_authenticate(user=user)
    return client, user


# ═════════════════════════════════════════════════════
# RAG Instance Endpoints
# ═════════════════════════════════════════════════════
class RAGInstanceListCreateViewTest(TestCase):
    def test_list_instances_200_for_authenticated(self):
        RAGInstanceFactory(is_public=True, slug="pub-1")
        client, _ = _user_client()
        resp = client.get(f"{BASE_URL}/instances/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data["data"]), 1)

    def test_list_instances_401_unauthenticated(self):
        resp = APIClient().get(f"{BASE_URL}/instances/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_instance_201_admin(self):
        client, user = _admin_client()
        # Need a provider
        inst = RAGInstanceFactory()
        provider_id = str(inst.provider.id)
        resp = client.post(f"{BASE_URL}/instances/", {
            "name": "New Bot",
            "slug": "new-bot",
            "system_prompt": "You are helpful",
            "provider_id": provider_id,
        }, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["data"]["name"], "New Bot")

    def test_create_instance_403_non_admin(self):
        client, _ = _user_client()
        resp = client.post(f"{BASE_URL}/instances/", {
            "name": "Test",
            "slug": "test",
            "system_prompt": "x",
            "provider_id": "00000000-0000-0000-0000-000000000000",
        }, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class RAGInstanceDetailViewTest(TestCase):
    def test_get_instance_200(self):
        inst = RAGInstanceFactory(slug="my-bot", is_public=True)
        client, _ = _user_client()
        resp = client.get(f"{BASE_URL}/instances/{inst.slug}/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["data"]["slug"], "my-bot")

    def test_get_instance_404(self):
        client, _ = _user_client()
        resp = client.get(f"{BASE_URL}/instances/nonexistent/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_instance_200_admin(self):
        inst = RAGInstanceFactory(slug="edit-me")
        client, _ = _admin_client()
        resp = client.patch(
            f"{BASE_URL}/instances/{inst.slug}/",
            {"name": "Updated Name"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["data"]["name"], "Updated Name")

    def test_patch_instance_403_non_admin(self):
        inst = RAGInstanceFactory(slug="no-edit")
        client, _ = _user_client()
        resp = client.patch(
            f"{BASE_URL}/instances/{inst.slug}/",
            {"name": "Hacked"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_instance_204_admin(self):
        inst = RAGInstanceFactory(slug="del-me")
        client, _ = _admin_client()
        resp = client.delete(f"{BASE_URL}/instances/{inst.slug}/")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        inst.refresh_from_db()
        self.assertTrue(inst.is_deleted)

    def test_delete_instance_403_non_admin(self):
        inst = RAGInstanceFactory(slug="no-del")
        client, _ = _user_client()
        resp = client.delete(f"{BASE_URL}/instances/{inst.slug}/")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class RAGInstanceConfigViewTest(TestCase):
    def test_update_config_200(self):
        inst = RAGInstanceFactory(slug="cfg-bot")
        client, _ = _admin_client()
        resp = client.patch(
            f"{BASE_URL}/instances/{inst.slug}/config/",
            {
                "config_type": "retrieval",
                "config": {"top_k_vector": 20},
                "reason": "tuning",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_update_config_403_non_admin(self):
        inst = RAGInstanceFactory(slug="cfg-nope")
        client, _ = _user_client()
        resp = client.patch(
            f"{BASE_URL}/instances/{inst.slug}/config/",
            {"config_type": "retrieval", "config": {}},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class RAGInstanceCloneViewTest(TestCase):
    def test_clone_instance_201(self):
        inst = RAGInstanceFactory(slug="original")
        client, _ = _admin_client()
        resp = client.post(
            f"{BASE_URL}/instances/{inst.slug}/clone/",
            {"new_name": "Clone Bot", "new_slug": "clone-bot"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["data"]["slug"], "clone-bot")

    def test_clone_403_non_admin(self):
        inst = RAGInstanceFactory(slug="orig-na")
        client, _ = _user_client()
        resp = client.post(
            f"{BASE_URL}/instances/{inst.slug}/clone/",
            {"new_name": "C", "new_slug": "c"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class RAGInstanceKBViewTest(TestCase):
    def test_list_instance_kbs_200(self):
        inst = RAGInstanceFactory(slug="kb-list")
        client, _ = _admin_client()
        resp = client.get(f"{BASE_URL}/instances/{inst.slug}/knowledge-bases/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_assign_kb_201(self):
        inst = RAGInstanceFactory(slug="kb-assign")
        kb = KnowledgeBaseFactory()
        client, _ = _admin_client()
        resp = client.post(
            f"{BASE_URL}/instances/{inst.slug}/knowledge-bases/",
            {"knowledge_base_id": str(kb.id), "priority": 1},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


class RAGInstanceSkillViewTest(TestCase):
    def test_list_instance_skills_200(self):
        inst = RAGInstanceFactory(slug="sk-list")
        client, _ = _admin_client()
        resp = client.get(f"{BASE_URL}/instances/{inst.slug}/skills/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_assign_skill_201(self):
        inst = RAGInstanceFactory(slug="sk-assign")
        skill = RAGSkillFactory()
        client, _ = _admin_client()
        resp = client.post(
            f"{BASE_URL}/instances/{inst.slug}/skills/",
            {"skill_id": str(skill.id)},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


# ═════════════════════════════════════════════════════
# Knowledge Base Endpoints
# ═════════════════════════════════════════════════════
class KnowledgeBaseListCreateViewTest(TestCase):
    def test_list_kbs_200_admin(self):
        KnowledgeBaseFactory()
        client, _ = _admin_client()
        resp = client.get(f"{BASE_URL}/knowledge-bases/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data["data"]), 1)

    def test_list_kbs_403_non_admin(self):
        client, _ = _user_client()
        resp = client.get(f"{BASE_URL}/knowledge-bases/")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_kb_201(self):
        client, _ = _admin_client()
        resp = client.post(f"{BASE_URL}/knowledge-bases/", {
            "name": "Product Docs",
            "slug": "product-docs",
        }, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["data"]["slug"], "product-docs")


class KnowledgeBaseDetailViewTest(TestCase):
    def test_get_kb_200(self):
        kb = KnowledgeBaseFactory(slug="kb-det")
        client, _ = _admin_client()
        resp = client.get(f"{BASE_URL}/knowledge-bases/{kb.slug}/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_kb_404(self):
        client, _ = _admin_client()
        resp = client.get(f"{BASE_URL}/knowledge-bases/nope/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_kb_204(self):
        kb = KnowledgeBaseFactory(slug="kb-del")
        client, _ = _admin_client()
        resp = client.delete(f"{BASE_URL}/knowledge-bases/{kb.slug}/")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class DocumentListViewTest(TestCase):
    def test_list_documents_200(self):
        kb = KnowledgeBaseFactory(slug="kb-docs")
        DocumentFactory(knowledge_base=kb)
        client, _ = _admin_client()
        resp = client.get(f"{BASE_URL}/knowledge-bases/{kb.slug}/documents/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["data"]), 1)

    def test_list_documents_filter_by_image(self):
        kb = KnowledgeBaseFactory(slug="kb-img-filter")
        DocumentFactory(knowledge_base=kb, is_image=False)
        DocumentFactory(knowledge_base=kb, is_image=True)
        client, _ = _admin_client()
        resp = client.get(f"{BASE_URL}/knowledge-bases/{kb.slug}/documents/?is_image=true")
        self.assertEqual(len(resp.data["data"]), 1)


class DocumentTextViewTest(TestCase):
    @patch("tasks.graph_rag_tasks.task_process_document")
    def test_add_text_document_201(self, mock_task):
        mock_task.delay = MagicMock()
        kb = KnowledgeBaseFactory(slug="kb-text")
        client, _ = _admin_client()
        resp = client.post(
            f"{BASE_URL}/knowledge-bases/{kb.slug}/documents/text/",
            {"title": "FAQ", "content_text": "Some content"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


class DocumentDetailViewTest(TestCase):
    def test_get_document_200(self):
        doc = DocumentFactory()
        client, _ = _admin_client()
        resp = client.get(f"{BASE_URL}/documents/{doc.id}/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_document_404(self):
        client, _ = _admin_client()
        resp = client.get(f"{BASE_URL}/documents/00000000-0000-0000-0000-000000000000/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_document_204(self):
        doc = DocumentFactory()
        client, _ = _admin_client()
        resp = client.delete(f"{BASE_URL}/documents/{doc.id}/")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class DocumentChunkListViewTest(TestCase):
    def test_list_chunks_200(self):
        doc = DocumentFactory()
        DocumentChunkFactory(document=doc)
        client, _ = _admin_client()
        resp = client.get(f"{BASE_URL}/documents/{doc.id}/chunks/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["data"]), 1)


# ═════════════════════════════════════════════════════
# Chat Endpoints
# ═════════════════════════════════════════════════════
class ChatQueryViewTest(TestCase):
    @patch("apps.graph_rag.views.chat_views.PipelineService")
    def test_chat_query_200(self, mock_pipeline):
        mock_pipeline.process_query.return_value = {
            "answer": "Hello!",
            "sources": [],
            "conversation_id": "some-id",
        }
        inst = RAGInstanceFactory(slug="chat-bot")
        client, user = _user_client()
        resp = client.post(
            f"{BASE_URL}/instances/{inst.slug}/chat/",
            {"query": "Hello"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_chat_query_401_unauthenticated(self):
        inst = RAGInstanceFactory(slug="chat-anon")
        resp = APIClient().post(
            f"{BASE_URL}/instances/{inst.slug}/chat/",
            {"query": "Hello"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_chat_query_404_nonexistent_instance(self):
        client, _ = _user_client()
        resp = client.post(
            f"{BASE_URL}/instances/nonexistent/chat/",
            {"query": "Hello"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class ConversationListViewTest(TestCase):
    def test_list_conversations_200(self):
        inst = RAGInstanceFactory(slug="conv-list")
        client, user = _user_client()
        RAGConversationFactory(rag_instance=inst, user=user)
        resp = client.get(f"{BASE_URL}/instances/{inst.slug}/conversations/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["data"]), 1)


class ConversationDetailViewTest(TestCase):
    def test_get_messages_200(self):
        client, user = _user_client()
        inst = RAGInstanceFactory(slug="conv-detail")
        conv = RAGConversationFactory(rag_instance=inst, user=user)
        RAGMessageFactory(conversation=conv, role="user", content="Hi")
        resp = client.get(
            f"{BASE_URL}/instances/{inst.slug}/conversations/{conv.id}/"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["data"]), 1)

    def test_delete_conversation_204(self):
        client, user = _user_client()
        inst = RAGInstanceFactory(slug="conv-del")
        conv = RAGConversationFactory(rag_instance=inst, user=user)
        resp = client.delete(
            f"{BASE_URL}/instances/{inst.slug}/conversations/{conv.id}/"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_messages_404_wrong_user(self):
        client, user = _user_client()
        inst = RAGInstanceFactory(slug="conv-wrong")
        other = UserFactory()
        conv = RAGConversationFactory(rag_instance=inst, user=other)
        resp = client.get(
            f"{BASE_URL}/instances/{inst.slug}/conversations/{conv.id}/"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class MessageFeedbackViewTest(TestCase):
    def test_feedback_200(self):
        msg = RAGMessageFactory()
        client, _ = _user_client()
        resp = client.post(
            f"{BASE_URL}/messages/{msg.id}/feedback/",
            {"feedback": "positive"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


# ═════════════════════════════════════════════════════
# Access Endpoints
# ═════════════════════════════════════════════════════
class AccessPermissionListCreateViewTest(TestCase):
    def test_list_access_200(self):
        inst = RAGInstanceFactory(slug="acc-list")
        RAGAccessPermissionFactory(rag_instance=inst)
        client, _ = _admin_client()
        resp = client.get(f"{BASE_URL}/instances/{inst.slug}/access/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["data"]), 1)

    def test_grant_access_201(self):
        inst = RAGInstanceFactory(slug="acc-grant")
        target_user = UserFactory()
        client, _ = _admin_client()
        resp = client.post(
            f"{BASE_URL}/instances/{inst.slug}/access/",
            {
                "user_id": str(target_user.id),
                "access_level": "use",
                "daily_query_limit": 50,
                "monthly_token_limit": 500000,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_grant_access_403_non_admin(self):
        inst = RAGInstanceFactory(slug="acc-deny")
        client, _ = _user_client()
        resp = client.post(
            f"{BASE_URL}/instances/{inst.slug}/access/",
            {"user_id": "fake", "access_level": "use"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class AccessPermissionDeleteViewTest(TestCase):
    def test_delete_access_204(self):
        inst = RAGInstanceFactory(slug="acc-del")
        perm = RAGAccessPermissionFactory(rag_instance=inst)
        client, _ = _admin_client()
        resp = client.delete(f"{BASE_URL}/instances/{inst.slug}/access/{perm.id}/")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_access_404(self):
        inst = RAGInstanceFactory(slug="acc-del-nf")
        client, _ = _admin_client()
        resp = client.delete(
            f"{BASE_URL}/instances/{inst.slug}/access/00000000-0000-0000-0000-000000000000/"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class MyAccessViewTest(TestCase):
    def test_my_access_with_permission(self):
        inst = RAGInstanceFactory(slug="my-acc")
        client, user = _user_client()
        RAGAccessPermissionFactory(rag_instance=inst, user=user)
        resp = client.get(f"{BASE_URL}/instances/{inst.slug}/my-access/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_my_access_public_instance(self):
        inst = RAGInstanceFactory(slug="my-pub", is_public=True)
        client, _ = _user_client()
        resp = client.get(f"{BASE_URL}/instances/{inst.slug}/my-access/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data["data"]["has_access"])


# ═════════════════════════════════════════════════════
# Analytics Endpoints
# ═════════════════════════════════════════════════════
class InstanceAnalyticsViewTest(TestCase):
    def test_analytics_200_admin(self):
        inst = RAGInstanceFactory(slug="ana-bot")
        client, _ = _admin_client()
        resp = client.get(f"{BASE_URL}/instances/{inst.slug}/analytics/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("total_queries", resp.data["data"])

    def test_analytics_403_non_admin(self):
        inst = RAGInstanceFactory(slug="ana-deny")
        client, _ = _user_client()
        resp = client.get(f"{BASE_URL}/instances/{inst.slug}/analytics/")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class UsageLogListViewTest(TestCase):
    def test_usage_logs_200(self):
        inst = RAGInstanceFactory(slug="log-bot")
        RAGUsageLogFactory(rag_instance=inst)
        client, _ = _admin_client()
        resp = client.get(f"{BASE_URL}/instances/{inst.slug}/usage-logs/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["data"]), 1)


class ConfigHistoryListViewTest(TestCase):
    def test_config_history_200(self):
        inst = RAGInstanceFactory(slug="hist-bot")
        RAGConfigHistoryFactory(rag_instance=inst)
        client, _ = _admin_client()
        resp = client.get(f"{BASE_URL}/instances/{inst.slug}/config-history/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["data"]), 1)

    def test_config_history_403_non_admin(self):
        inst = RAGInstanceFactory(slug="hist-deny")
        client, _ = _user_client()
        resp = client.get(f"{BASE_URL}/instances/{inst.slug}/config-history/")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
