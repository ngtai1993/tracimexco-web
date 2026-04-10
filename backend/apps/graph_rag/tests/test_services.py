from unittest.mock import patch, MagicMock
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.graph_rag.constants import DEFAULT_RETRIEVAL_CONFIG, DEFAULT_GENERATION_CONFIG
from apps.graph_rag.exceptions import RAGConversationNotFound, DocumentProcessingError
from apps.graph_rag.models import (
    RAGInstance,
    RAGInstanceKnowledgeBase,
    RAGInstanceSkill,
    RAGConfigHistory,
    KnowledgeBase,
    Document,
    RAGConversation,
    RAGMessage,
    RAGAccessPermission,
    RAGUsageLog,
)
from apps.graph_rag.services.rag_instance_service import RAGInstanceService
from apps.graph_rag.services.knowledge_base_service import KnowledgeBaseService
from apps.graph_rag.services.conversation_service import ConversationService
from apps.graph_rag.services.access_service import AccessService
from apps.graph_rag.services.analytics_service import AnalyticsService
from apps.graph_rag.tests.factories import (
    RAGInstanceFactory,
    KnowledgeBaseFactory,
    DocumentFactory,
    RAGSkillFactory,
    RAGConversationFactory,
    RAGMessageFactory,
    RAGAccessPermissionFactory,
    UserFactory,
    AdminUserFactory,
)


# ─────────────────────────────────────────────────────
# RAGInstanceService
# ─────────────────────────────────────────────────────
class RAGInstanceServiceCreateTest(TestCase):
    def setUp(self):
        self.provider = RAGInstanceFactory().provider  # reuse existing provider
        self.user = AdminUserFactory()

    def test_create_merges_retrieval_config_with_defaults(self):
        custom = {"top_k_vector": 20}
        inst = RAGInstanceService.create(
            name="Test",
            slug="test-create",
            system_prompt="Hello",
            provider_id=self.provider.id,
            retrieval_config=custom,
            created_by=self.user,
        )
        expected = {**DEFAULT_RETRIEVAL_CONFIG, **custom}
        self.assertEqual(inst.retrieval_config, expected)

    def test_create_merges_generation_config_with_defaults(self):
        custom = {"temperature": 0.3}
        inst = RAGInstanceService.create(
            name="Test Gen",
            slug="test-gen",
            system_prompt="Hello",
            provider_id=self.provider.id,
            generation_config=custom,
            created_by=self.user,
        )
        expected = {**DEFAULT_GENERATION_CONFIG, **custom}
        self.assertEqual(inst.generation_config, expected)

    def test_create_uses_full_defaults_when_no_config(self):
        inst = RAGInstanceService.create(
            name="Defaults",
            slug="test-defaults",
            system_prompt="Hello",
            provider_id=self.provider.id,
            created_by=self.user,
        )
        self.assertEqual(inst.retrieval_config, DEFAULT_RETRIEVAL_CONFIG)
        self.assertEqual(inst.generation_config, DEFAULT_GENERATION_CONFIG)


class RAGInstanceServiceUpdateConfigTest(TestCase):
    def setUp(self):
        self.instance = RAGInstanceFactory()
        self.user = AdminUserFactory()

    def test_update_retrieval_config_deep_merges(self):
        new = {"top_k_vector": 50}
        updated = RAGInstanceService.update_config(
            instance_id=self.instance.id,
            config_type="retrieval",
            new_config=new,
            changed_by=self.user,
            reason="tuning",
        )
        self.assertEqual(updated.retrieval_config["top_k_vector"], 50)
        # Other keys preserved
        self.assertIn("search_strategy", updated.retrieval_config)

    def test_update_creates_config_history(self):
        RAGInstanceService.update_config(
            instance_id=self.instance.id,
            config_type="retrieval",
            new_config={"top_k_vector": 30},
            changed_by=self.user,
            reason="test reason",
        )
        history = RAGConfigHistory.objects.filter(rag_instance=self.instance)
        self.assertEqual(history.count(), 1)
        self.assertEqual(history.first().config_type, "retrieval")
        self.assertEqual(history.first().reason, "test reason")

    def test_update_generation_config(self):
        updated = RAGInstanceService.update_config(
            instance_id=self.instance.id,
            config_type="generation",
            new_config={"temperature": 0.1},
            changed_by=self.user,
        )
        self.assertEqual(updated.generation_config["temperature"], 0.1)

    def test_update_system_prompt(self):
        updated = RAGInstanceService.update_config(
            instance_id=self.instance.id,
            config_type="system_prompt",
            new_config={"system_prompt": "New prompt"},
            changed_by=self.user,
        )
        self.assertEqual(updated.system_prompt, "New prompt")

    def test_update_invalid_config_type_raises(self):
        with self.assertRaises(ValueError):
            RAGInstanceService.update_config(
                instance_id=self.instance.id,
                config_type="invalid",
                new_config={},
                changed_by=self.user,
            )


class RAGInstanceServiceCloneTest(TestCase):
    def test_clone_copies_config(self):
        source = RAGInstanceFactory(
            retrieval_config={**DEFAULT_RETRIEVAL_CONFIG, "top_k_vector": 99}
        )
        clone = RAGInstanceService.clone(
            source_id=source.id,
            new_name="Clone",
            new_slug="clone-slug",
        )
        self.assertEqual(clone.name, "Clone")
        self.assertEqual(clone.slug, "clone-slug")
        self.assertEqual(clone.retrieval_config["top_k_vector"], 99)
        self.assertEqual(clone.provider, source.provider)

    def test_clone_copies_kb_assignments(self):
        source = RAGInstanceFactory()
        kb = KnowledgeBaseFactory()
        RAGInstanceKnowledgeBase.objects.create(
            rag_instance=source, knowledge_base=kb, priority=2
        )
        clone = RAGInstanceService.clone(
            source_id=source.id, new_name="C2", new_slug="c2"
        )
        assignments = RAGInstanceKnowledgeBase.objects.filter(rag_instance=clone)
        self.assertEqual(assignments.count(), 1)
        self.assertEqual(assignments.first().knowledge_base, kb)
        self.assertEqual(assignments.first().priority, 2)

    def test_clone_copies_skill_assignments(self):
        source = RAGInstanceFactory()
        skill = RAGSkillFactory()
        RAGInstanceSkill.objects.create(
            rag_instance=source, skill=skill, config_override={"k": "v"}
        )
        clone = RAGInstanceService.clone(
            source_id=source.id, new_name="C3", new_slug="c3"
        )
        assignments = RAGInstanceSkill.objects.filter(rag_instance=clone)
        self.assertEqual(assignments.count(), 1)
        self.assertEqual(assignments.first().config_override, {"k": "v"})


class RAGInstanceServiceAssignTest(TestCase):
    def test_assign_knowledge_base(self):
        instance = RAGInstanceFactory()
        kb = KnowledgeBaseFactory()
        assignment = RAGInstanceService.assign_knowledge_base(
            instance_id=instance.id, kb_id=kb.id, priority=3
        )
        self.assertEqual(assignment.priority, 3)

    def test_assign_skill(self):
        instance = RAGInstanceFactory()
        skill = RAGSkillFactory()
        assignment = RAGInstanceService.assign_skill(
            instance_id=instance.id,
            skill_id=skill.id,
            config_override={"timeout": 30},
        )
        self.assertEqual(assignment.config_override, {"timeout": 30})


class RAGInstanceServiceSoftDeleteTest(TestCase):
    def test_soft_delete_cascades_to_assignments(self):
        instance = RAGInstanceFactory()
        kb = KnowledgeBaseFactory()
        skill = RAGSkillFactory()
        RAGInstanceKnowledgeBase.objects.create(
            rag_instance=instance, knowledge_base=kb, priority=1
        )
        RAGInstanceSkill.objects.create(rag_instance=instance, skill=skill)

        RAGInstanceService.soft_delete(instance.id)

        instance.refresh_from_db()
        self.assertTrue(instance.is_deleted)
        self.assertTrue(
            RAGInstanceKnowledgeBase.objects.get(
                rag_instance=instance
            ).is_deleted
        )
        self.assertTrue(
            RAGInstanceSkill.objects.get(rag_instance=instance).is_deleted
        )


# ─────────────────────────────────────────────────────
# KnowledgeBaseService
# ─────────────────────────────────────────────────────
class KnowledgeBaseServiceCreateTest(TestCase):
    def test_create_kb(self):
        user = AdminUserFactory()
        kb = KnowledgeBaseService.create_kb(
            name="Docs",
            slug="docs-kb",
            chunk_strategy="semantic",
            chunk_size=1024,
            created_by=user,
        )
        self.assertEqual(kb.name, "Docs")
        self.assertEqual(kb.chunk_strategy, "semantic")
        self.assertEqual(kb.chunk_size, 1024)


class KnowledgeBaseServiceUploadDocTest(TestCase):
    def setUp(self):
        self.kb = KnowledgeBaseFactory(document_count=0, image_count=0)

    @patch("apps.graph_rag.services.knowledge_base_service.task_process_document", create=True)
    def test_upload_pdf_creates_document(self, mock_task):
        mock_task.delay = MagicMock()
        file = SimpleUploadedFile("test.pdf", b"fake-pdf-content", content_type="application/pdf")
        doc = KnowledgeBaseService.upload_document(
            knowledge_base_id=self.kb.id,
            title="Test PDF",
            file=file,
        )
        self.assertEqual(doc.title, "Test PDF")
        self.assertEqual(doc.source_type, "file_upload")
        self.assertFalse(doc.is_image)
        self.assertEqual(doc.processing_status, "pending")

    @patch("apps.graph_rag.services.knowledge_base_service.task_process_document", create=True)
    def test_upload_image_sets_is_image(self, mock_task):
        mock_task.delay = MagicMock()
        file = SimpleUploadedFile("photo.jpg", b"fake-img", content_type="image/jpeg")
        doc = KnowledgeBaseService.upload_document(
            knowledge_base_id=self.kb.id,
            title="Test Image",
            file=file,
        )
        self.assertTrue(doc.is_image)
        self.assertEqual(doc.source_type, "image_upload")

    @patch("apps.graph_rag.services.knowledge_base_service.task_process_document", create=True)
    def test_upload_increments_document_count(self, mock_task):
        mock_task.delay = MagicMock()
        file = SimpleUploadedFile("test.txt", b"hello", content_type="text/plain")
        KnowledgeBaseService.upload_document(
            knowledge_base_id=self.kb.id, title="T", file=file,
        )
        self.kb.refresh_from_db()
        self.assertEqual(self.kb.document_count, 1)

    @patch("apps.graph_rag.services.knowledge_base_service.task_process_document", create=True)
    def test_upload_image_increments_image_count(self, mock_task):
        mock_task.delay = MagicMock()
        file = SimpleUploadedFile("img.png", b"data", content_type="image/png")
        KnowledgeBaseService.upload_document(
            knowledge_base_id=self.kb.id, title="I", file=file,
        )
        self.kb.refresh_from_db()
        self.assertEqual(self.kb.image_count, 1)

    def test_upload_unsupported_extension_raises(self):
        file = SimpleUploadedFile("data.exe", b"bad", content_type="application/octet-stream")
        with self.assertRaises(DocumentProcessingError):
            KnowledgeBaseService.upload_document(
                knowledge_base_id=self.kb.id, title="Bad", file=file,
            )

    def test_upload_too_large_raises(self):
        file = SimpleUploadedFile("big.pdf", b"x", content_type="application/pdf")
        file.size = 51 * 1024 * 1024  # 51 MB
        with self.assertRaises(DocumentProcessingError):
            KnowledgeBaseService.upload_document(
                knowledge_base_id=self.kb.id, title="Big", file=file,
            )


class KnowledgeBaseServiceTextDocTest(TestCase):
    @patch("tasks.graph_rag_tasks.task_process_document")
    def test_add_text_document(self, mock_task):
        mock_task.delay = MagicMock()
        kb = KnowledgeBaseFactory(document_count=0)
        doc = KnowledgeBaseService.add_text_document(
            knowledge_base_id=kb.id,
            title="FAQ",
            content_text="Some text content",
        )
        self.assertEqual(doc.source_type, "text")
        self.assertEqual(doc.content_text, "Some text content")
        kb.refresh_from_db()
        self.assertEqual(kb.document_count, 1)


class KnowledgeBaseServiceSoftDeleteDocTest(TestCase):
    def test_soft_delete_document_decrements_count(self):
        kb = KnowledgeBaseFactory(document_count=3, total_chunks=10)
        doc = DocumentFactory(
            knowledge_base=kb, is_image=False, chunk_count=5
        )
        KnowledgeBaseService.soft_delete_document(doc.id)
        doc.refresh_from_db()
        self.assertTrue(doc.is_deleted)
        kb.refresh_from_db()
        self.assertEqual(kb.document_count, 2)
        self.assertEqual(kb.total_chunks, 5)

    def test_soft_delete_image_doc_decrements_image_count(self):
        kb = KnowledgeBaseFactory(image_count=2)
        doc = DocumentFactory(knowledge_base=kb, is_image=True)
        KnowledgeBaseService.soft_delete_document(doc.id)
        kb.refresh_from_db()
        self.assertEqual(kb.image_count, 1)


class KnowledgeBaseServiceSoftDeleteKBTest(TestCase):
    def test_soft_delete_kb_cascades_documents(self):
        kb = KnowledgeBaseFactory()
        doc1 = DocumentFactory(knowledge_base=kb)
        doc2 = DocumentFactory(knowledge_base=kb)

        KnowledgeBaseService.soft_delete_kb(kb.id)

        kb.refresh_from_db()
        self.assertTrue(kb.is_deleted)
        doc1.refresh_from_db()
        self.assertTrue(doc1.is_deleted)
        doc2.refresh_from_db()
        self.assertTrue(doc2.is_deleted)


# ─────────────────────────────────────────────────────
# ConversationService
# ─────────────────────────────────────────────────────
class ConversationServiceTest(TestCase):
    def test_get_conversation_messages(self):
        conv = RAGConversationFactory()
        RAGMessageFactory(conversation=conv, role="user", content="Hello")
        RAGMessageFactory(conversation=conv, role="assistant", content="Hi there")

        messages = ConversationService.get_conversation_messages(
            str(conv.id), str(conv.user.id)
        )
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "user")
        self.assertEqual(messages[1]["role"], "assistant")

    def test_get_messages_wrong_user_raises(self):
        conv = RAGConversationFactory()
        other_user = UserFactory()
        with self.assertRaises(RAGConversationNotFound):
            ConversationService.get_conversation_messages(
                str(conv.id), str(other_user.id)
            )

    def test_update_feedback(self):
        msg = RAGMessageFactory()
        ConversationService.update_feedback(str(msg.id), "thumbs_up", "Great answer")
        msg.refresh_from_db()
        self.assertEqual(msg.feedback, "thumbs_up")
        self.assertEqual(msg.feedback_comment, "Great answer")

    def test_soft_delete_conversation(self):
        conv = RAGConversationFactory()
        ConversationService.soft_delete_conversation(
            str(conv.id), str(conv.user.id)
        )
        conv.refresh_from_db()
        self.assertTrue(conv.is_deleted)

    def test_soft_delete_conversation_wrong_user_raises(self):
        conv = RAGConversationFactory()
        other_user = UserFactory()
        with self.assertRaises(RAGConversationNotFound):
            ConversationService.soft_delete_conversation(
                str(conv.id), str(other_user.id)
            )


# ─────────────────────────────────────────────────────
# AccessService
# ─────────────────────────────────────────────────────
class AccessServiceGrantTest(TestCase):
    def test_grant_access(self):
        instance = RAGInstanceFactory()
        user = UserFactory()
        admin = AdminUserFactory()
        perm = AccessService.grant_access(
            instance_id=str(instance.id),
            user_id=str(user.id),
            access_level="use",
            daily_query_limit=50,
            monthly_token_limit=500_000,
            granted_by=admin,
        )
        self.assertEqual(perm.access_level, "use")
        self.assertEqual(perm.daily_query_limit, 50)
        self.assertEqual(perm.monthly_token_limit, 500_000)


class AccessServiceQuotaTest(TestCase):
    def test_check_quota_no_perm_passes(self):
        """Public instances / admin — no quota check needed."""
        instance = RAGInstanceFactory()
        user = UserFactory()
        # Should not raise
        AccessService.check_quota(
            instance_id=str(instance.id), user_id=str(user.id)
        )

    def test_check_quota_under_limit_passes(self):
        instance = RAGInstanceFactory()
        user = UserFactory()
        RAGAccessPermissionFactory(
            rag_instance=instance, user=user, daily_query_limit=10
        )
        # 0 queries today — should pass
        AccessService.check_quota(
            instance_id=str(instance.id), user_id=str(user.id)
        )


# ─────────────────────────────────────────────────────
# AnalyticsService
# ─────────────────────────────────────────────────────
class AnalyticsServiceTest(TestCase):
    def test_log_usage(self):
        instance = RAGInstanceFactory()
        user = UserFactory()
        AnalyticsService.log_usage({
            "rag_instance_id": str(instance.id),
            "user_id": str(user.id),
            "query": "test query",
            "tokens_in": 100,
            "tokens_out": 200,
            "latency_ms": 500,
            "sources_count": 3,
        })
        self.assertEqual(RAGUsageLog.objects.count(), 1)
        log = RAGUsageLog.objects.first()
        self.assertEqual(log.tokens_in, 100)

    def test_get_instance_analytics_empty(self):
        instance = RAGInstanceFactory()
        result = AnalyticsService.get_instance_analytics(str(instance.id))
        self.assertEqual(result["total_queries"], 0)
        self.assertEqual(result["unique_users"], 0)
        self.assertEqual(result["total_tokens_in"], 0)

    def test_get_instance_analytics_with_data(self):
        instance = RAGInstanceFactory()
        user = UserFactory()
        for _ in range(3):
            AnalyticsService.log_usage({
                "rag_instance_id": str(instance.id),
                "user_id": str(user.id),
                "query": "q",
                "tokens_in": 10,
                "tokens_out": 20,
                "latency_ms": 100,
            })
        result = AnalyticsService.get_instance_analytics(str(instance.id))
        self.assertEqual(result["total_queries"], 3)
        self.assertEqual(result["unique_users"], 1)
        self.assertEqual(result["total_tokens_in"], 30)
        self.assertEqual(result["total_tokens_out"], 60)
