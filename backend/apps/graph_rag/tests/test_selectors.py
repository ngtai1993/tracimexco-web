from django.test import TestCase

from apps.graph_rag.exceptions import (
    RAGInstanceNotFound,
    KnowledgeBaseNotFound,
    DocumentNotFound,
    RAGConversationNotFound,
)
from apps.graph_rag.models import (
    RAGInstanceKnowledgeBase,
    RAGInstanceSkill,
)
from apps.graph_rag.selectors import RAGSelector
from apps.graph_rag.tests.factories import (
    RAGInstanceFactory,
    KnowledgeBaseFactory,
    DocumentFactory,
    ImageDocumentFactory,
    DocumentChunkFactory,
    ImageChunkFactory,
    KnowledgeGraphFactory,
    RAGSkillFactory,
    RAGConversationFactory,
    RAGMessageFactory,
    RAGAccessPermissionFactory,
    UserFactory,
)


# ─────────────────────────────────────────────────────
# RAG Instance selectors
# ─────────────────────────────────────────────────────
class RAGSelectorInstanceTest(TestCase):
    def test_get_instance(self):
        instance = RAGInstanceFactory()
        result = RAGSelector.get_instance(instance.id)
        self.assertEqual(result.id, instance.id)

    def test_get_instance_not_found_raises(self):
        with self.assertRaises(RAGInstanceNotFound):
            RAGSelector.get_instance("00000000-0000-0000-0000-000000000000")

    def test_get_instance_soft_deleted_raises(self):
        instance = RAGInstanceFactory()
        instance.soft_delete()
        with self.assertRaises(RAGInstanceNotFound):
            RAGSelector.get_instance(instance.id)

    def test_get_instance_by_slug(self):
        instance = RAGInstanceFactory(slug="my-bot")
        result = RAGSelector.get_instance_by_slug("my-bot")
        self.assertEqual(result.id, instance.id)

    def test_get_instance_by_slug_not_found(self):
        with self.assertRaises(RAGInstanceNotFound):
            RAGSelector.get_instance_by_slug("nonexistent")

    def test_list_instances_returns_active_only(self):
        RAGInstanceFactory(is_active=True)
        RAGInstanceFactory(is_active=False)
        result = RAGSelector.list_instances()
        self.assertEqual(result.count(), 1)

    def test_list_instances_include_inactive(self):
        RAGInstanceFactory(is_active=True)
        RAGInstanceFactory(is_active=False)
        result = RAGSelector.list_instances(include_inactive=True)
        self.assertEqual(result.count(), 2)

    def test_list_instances_excludes_soft_deleted(self):
        inst = RAGInstanceFactory()
        inst.soft_delete()
        result = RAGSelector.list_instances()
        self.assertEqual(result.count(), 0)

    def test_list_instances_user_sees_public(self):
        user = UserFactory()
        RAGInstanceFactory(is_public=True)
        RAGInstanceFactory(is_public=False)
        result = RAGSelector.list_instances(user=user)
        self.assertEqual(result.count(), 1)

    def test_list_instances_user_sees_own(self):
        user = UserFactory()
        RAGInstanceFactory(is_public=False, created_by=user)
        result = RAGSelector.list_instances(user=user)
        self.assertEqual(result.count(), 1)

    def test_list_instances_user_sees_permitted(self):
        user = UserFactory()
        instance = RAGInstanceFactory(is_public=False)
        RAGAccessPermissionFactory(rag_instance=instance, user=user)
        result = RAGSelector.list_instances(user=user)
        self.assertEqual(result.count(), 1)


class RAGSelectorInstanceKBSkillTest(TestCase):
    def test_list_instance_kbs(self):
        instance = RAGInstanceFactory()
        kb = KnowledgeBaseFactory()
        RAGInstanceKnowledgeBase.objects.create(
            rag_instance=instance, knowledge_base=kb, priority=1
        )
        result = RAGSelector.list_instance_kbs(instance.id)
        self.assertEqual(result.count(), 1)

    def test_list_instance_skills(self):
        instance = RAGInstanceFactory()
        skill = RAGSkillFactory()
        RAGInstanceSkill.objects.create(rag_instance=instance, skill=skill)
        result = RAGSelector.list_instance_skills(instance.id)
        self.assertEqual(result.count(), 1)


# ─────────────────────────────────────────────────────
# Knowledge Base selectors
# ─────────────────────────────────────────────────────
class RAGSelectorKBTest(TestCase):
    def test_get_kb(self):
        kb = KnowledgeBaseFactory()
        result = RAGSelector.get_kb(kb.id)
        self.assertEqual(result.id, kb.id)

    def test_get_kb_not_found(self):
        with self.assertRaises(KnowledgeBaseNotFound):
            RAGSelector.get_kb("00000000-0000-0000-0000-000000000000")

    def test_get_kb_by_slug(self):
        kb = KnowledgeBaseFactory(slug="product-docs")
        result = RAGSelector.get_kb_by_slug("product-docs")
        self.assertEqual(result.id, kb.id)

    def test_get_kb_by_slug_not_found(self):
        with self.assertRaises(KnowledgeBaseNotFound):
            RAGSelector.get_kb_by_slug("nope")

    def test_list_kbs_active_only(self):
        KnowledgeBaseFactory(is_active=True)
        KnowledgeBaseFactory(is_active=False)
        result = RAGSelector.list_kbs()
        self.assertEqual(result.count(), 1)

    def test_list_kbs_include_inactive(self):
        KnowledgeBaseFactory(is_active=True)
        KnowledgeBaseFactory(is_active=False)
        result = RAGSelector.list_kbs(include_inactive=True)
        self.assertEqual(result.count(), 2)


# ─────────────────────────────────────────────────────
# Document selectors
# ─────────────────────────────────────────────────────
class RAGSelectorDocumentTest(TestCase):
    def test_list_documents(self):
        kb = KnowledgeBaseFactory()
        DocumentFactory(knowledge_base=kb)
        DocumentFactory(knowledge_base=kb)
        result = RAGSelector.list_documents(kb.id)
        self.assertEqual(result.count(), 2)

    def test_list_documents_filter_images(self):
        kb = KnowledgeBaseFactory()
        DocumentFactory(knowledge_base=kb, is_image=False)
        ImageDocumentFactory(knowledge_base=kb)
        self.assertEqual(RAGSelector.list_documents(kb.id, is_image=True).count(), 1)
        self.assertEqual(RAGSelector.list_documents(kb.id, is_image=False).count(), 1)

    def test_get_document(self):
        doc = DocumentFactory()
        result = RAGSelector.get_document(doc.id)
        self.assertEqual(result.id, doc.id)

    def test_get_document_not_found(self):
        with self.assertRaises(DocumentNotFound):
            RAGSelector.get_document("00000000-0000-0000-0000-000000000000")

    def test_list_chunks(self):
        doc = DocumentFactory()
        DocumentChunkFactory(document=doc, chunk_index=0)
        DocumentChunkFactory(document=doc, chunk_index=1)
        result = RAGSelector.list_chunks(doc.id)
        self.assertEqual(result.count(), 2)

    def test_list_chunks_filter_image(self):
        doc = DocumentFactory()
        DocumentChunkFactory(document=doc, is_image_chunk=False)
        ImageChunkFactory(document=doc)
        self.assertEqual(
            RAGSelector.list_chunks(doc.id, is_image_chunk=True).count(), 1
        )
        self.assertEqual(
            RAGSelector.list_chunks(doc.id, is_image_chunk=False).count(), 1
        )


# ─────────────────────────────────────────────────────
# Graph selectors
# ─────────────────────────────────────────────────────
class RAGSelectorGraphTest(TestCase):
    def test_get_graph_exists(self):
        kb = KnowledgeBaseFactory()
        graph = KnowledgeGraphFactory(knowledge_base=kb)
        result = RAGSelector.get_graph(kb.id)
        self.assertEqual(result.id, graph.id)

    def test_get_graph_not_exists_returns_none(self):
        kb = KnowledgeBaseFactory()
        self.assertIsNone(RAGSelector.get_graph(kb.id))


# ─────────────────────────────────────────────────────
# Conversation selectors
# ─────────────────────────────────────────────────────
class RAGSelectorConversationTest(TestCase):
    def test_list_conversations(self):
        instance = RAGInstanceFactory()
        user = UserFactory()
        RAGConversationFactory(rag_instance=instance, user=user)
        RAGConversationFactory(rag_instance=instance, user=user)
        result = RAGSelector.list_conversations(
            instance_id=instance.id, user_id=user.id
        )
        self.assertEqual(result.count(), 2)

    def test_list_conversations_excludes_other_users(self):
        instance = RAGInstanceFactory()
        user = UserFactory()
        other = UserFactory()
        RAGConversationFactory(rag_instance=instance, user=user)
        RAGConversationFactory(rag_instance=instance, user=other)
        result = RAGSelector.list_conversations(
            instance_id=instance.id, user_id=user.id
        )
        self.assertEqual(result.count(), 1)

    def test_get_conversation(self):
        conv = RAGConversationFactory()
        result = RAGSelector.get_conversation(conv.id, conv.user.id)
        self.assertEqual(result.id, conv.id)

    def test_get_conversation_wrong_user_raises(self):
        conv = RAGConversationFactory()
        other = UserFactory()
        with self.assertRaises(RAGConversationNotFound):
            RAGSelector.get_conversation(conv.id, other.id)


# ─────────────────────────────────────────────────────
# Access selectors
# ─────────────────────────────────────────────────────
class RAGSelectorAccessTest(TestCase):
    def test_list_access_permissions(self):
        instance = RAGInstanceFactory()
        RAGAccessPermissionFactory(rag_instance=instance)
        RAGAccessPermissionFactory(rag_instance=instance)
        result = RAGSelector.list_access_permissions(instance.id)
        self.assertEqual(result.count(), 2)


# ─────────────────────────────────────────────────────
# Skills selectors
# ─────────────────────────────────────────────────────
class RAGSelectorSkillTest(TestCase):
    def test_list_skills_active_only(self):
        RAGSkillFactory(is_active=True)
        RAGSkillFactory(is_active=False)
        result = RAGSelector.list_skills()
        self.assertEqual(result.count(), 1)
