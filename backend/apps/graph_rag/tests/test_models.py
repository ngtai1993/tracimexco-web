from django.db import IntegrityError
from django.test import TestCase

from apps.graph_rag.constants import DEFAULT_RETRIEVAL_CONFIG, DEFAULT_GENERATION_CONFIG
from apps.graph_rag.models import (
    RAGInstance,
    RAGInstanceKnowledgeBase,
    KnowledgeBase,
    Document,
    DocumentChunk,
    KnowledgeGraph,
    GraphEntity,
    GraphRelationship,
    RAGSkill,
    RAGInstanceSkill,
    RAGConversation,
    RAGMessage,
    RAGAccessPermission,
)
from apps.graph_rag.tests.factories import (
    RAGInstanceFactory,
    KnowledgeBaseFactory,
    DocumentFactory,
    ImageDocumentFactory,
    DocumentChunkFactory,
    ImageChunkFactory,
    KnowledgeGraphFactory,
    GraphEntityFactory,
    RAGSkillFactory,
    RAGConversationFactory,
    RAGMessageFactory,
    RAGAccessPermissionFactory,
    UserFactory,
    AdminUserFactory,
)


# ─────────────────────────────────────────────────────
# RAGInstance
# ─────────────────────────────────────────────────────
class RAGInstanceModelTest(TestCase):
    def test_create_instance_saves_all_fields(self):
        instance = RAGInstanceFactory(name="Customer Support Bot", purpose="customer_support")
        db = RAGInstance.objects.get(pk=instance.pk)
        self.assertEqual(db.name, "Customer Support Bot")
        self.assertEqual(db.purpose, "customer_support")
        self.assertTrue(db.is_active)
        self.assertFalse(db.is_deleted)
        self.assertFalse(db.is_public)

    def test_str_returns_name(self):
        instance = RAGInstanceFactory(name="My RAG Bot")
        self.assertEqual(str(instance), "My RAG Bot")

    def test_slug_is_unique(self):
        RAGInstanceFactory(slug="my-rag")
        with self.assertRaises(IntegrityError):
            RAGInstanceFactory(slug="my-rag")

    def test_soft_delete_marks_is_deleted(self):
        instance = RAGInstanceFactory()
        instance.soft_delete()
        instance.refresh_from_db()
        self.assertTrue(instance.is_deleted)
        self.assertTrue(RAGInstance.objects.filter(pk=instance.pk).exists())

    def test_restore_after_soft_delete(self):
        instance = RAGInstanceFactory()
        instance.soft_delete()
        instance.restore()
        instance.refresh_from_db()
        self.assertFalse(instance.is_deleted)

    def test_empty_config_gets_defaults_on_save(self):
        instance = RAGInstanceFactory(retrieval_config={}, generation_config={})
        instance.refresh_from_db()
        self.assertEqual(instance.retrieval_config, DEFAULT_RETRIEVAL_CONFIG)
        self.assertEqual(instance.generation_config, DEFAULT_GENERATION_CONFIG)

    def test_images_enabled_property_false_by_default(self):
        instance = RAGInstanceFactory()
        self.assertFalse(instance.images_enabled)

    def test_images_enabled_property_true_when_set(self):
        config = {**DEFAULT_RETRIEVAL_CONFIG, "images_enabled": True}
        instance = RAGInstanceFactory(retrieval_config=config)
        self.assertTrue(instance.images_enabled)

    def test_provider_protect_on_delete(self):
        instance = RAGInstanceFactory()
        provider = instance.provider
        with self.assertRaises(Exception):
            provider.delete()


# ─────────────────────────────────────────────────────
# RAGInstanceKnowledgeBase (M2M through)
# ─────────────────────────────────────────────────────
class RAGInstanceKnowledgeBaseModelTest(TestCase):
    def test_assign_kb_to_instance(self):
        instance = RAGInstanceFactory()
        kb = KnowledgeBaseFactory()
        assignment = RAGInstanceKnowledgeBase.objects.create(
            rag_instance=instance, knowledge_base=kb, priority=1
        )
        self.assertEqual(assignment.rag_instance, instance)
        self.assertEqual(assignment.knowledge_base, kb)
        self.assertEqual(assignment.priority, 1)

    def test_unique_together_instance_kb(self):
        instance = RAGInstanceFactory()
        kb = KnowledgeBaseFactory()
        RAGInstanceKnowledgeBase.objects.create(
            rag_instance=instance, knowledge_base=kb, priority=1
        )
        with self.assertRaises(IntegrityError):
            RAGInstanceKnowledgeBase.objects.create(
                rag_instance=instance, knowledge_base=kb, priority=2
            )

    def test_str_contains_slugs(self):
        instance = RAGInstanceFactory(slug="my-rag")
        kb = KnowledgeBaseFactory(slug="my-kb")
        assignment = RAGInstanceKnowledgeBase.objects.create(
            rag_instance=instance, knowledge_base=kb, priority=1
        )
        self.assertIn("my-rag", str(assignment))
        self.assertIn("my-kb", str(assignment))


# ─────────────────────────────────────────────────────
# KnowledgeBase
# ─────────────────────────────────────────────────────
class KnowledgeBaseModelTest(TestCase):
    def test_create_kb_with_defaults(self):
        kb = KnowledgeBaseFactory()
        self.assertEqual(kb.chunk_strategy, "recursive")
        self.assertEqual(kb.chunk_size, 512)
        self.assertEqual(kb.chunk_overlap, 50)
        self.assertEqual(kb.document_count, 0)
        self.assertEqual(kb.image_count, 0)
        self.assertTrue(kb.is_active)

    def test_slug_is_unique(self):
        KnowledgeBaseFactory(slug="docs")
        with self.assertRaises(IntegrityError):
            KnowledgeBaseFactory(slug="docs")

    def test_str_returns_name(self):
        kb = KnowledgeBaseFactory(name="Product Docs")
        self.assertEqual(str(kb), "Product Docs")


# ─────────────────────────────────────────────────────
# Document
# ─────────────────────────────────────────────────────
class DocumentModelTest(TestCase):
    def test_create_text_document(self):
        doc = DocumentFactory(title="Tài liệu A", source_type="text")
        self.assertEqual(doc.title, "Tài liệu A")
        self.assertFalse(doc.is_image)
        self.assertEqual(doc.processing_status, "completed")

    def test_create_image_document(self):
        doc = ImageDocumentFactory()
        self.assertTrue(doc.is_image)
        self.assertNotEqual(doc.image_caption, "")
        self.assertIsInstance(doc.image_tags, list)
        self.assertTrue(len(doc.image_tags) > 0)

    def test_str_returns_title(self):
        doc = DocumentFactory(title="My Document")
        self.assertEqual(str(doc), "My Document")

    def test_document_belongs_to_kb(self):
        kb = KnowledgeBaseFactory()
        doc = DocumentFactory(knowledge_base=kb)
        self.assertEqual(doc.knowledge_base, kb)
        self.assertIn(doc, kb.documents.all())


# ─────────────────────────────────────────────────────
# DocumentChunk
# ─────────────────────────────────────────────────────
class DocumentChunkModelTest(TestCase):
    def test_create_text_chunk(self):
        chunk = DocumentChunkFactory()
        self.assertFalse(chunk.is_image_chunk)
        self.assertGreater(chunk.token_count, 0)

    def test_create_image_chunk(self):
        chunk = ImageChunkFactory()
        self.assertTrue(chunk.is_image_chunk)
        self.assertIn("image_url", chunk.metadata)

    def test_chunk_str_contains_title(self):
        doc = DocumentFactory(title="Important Doc")
        chunk = DocumentChunkFactory(document=doc, chunk_index=3)
        self.assertIn("Important Doc", str(chunk))
        self.assertIn("3", str(chunk))


# ─────────────────────────────────────────────────────
# KnowledgeGraph
# ─────────────────────────────────────────────────────
class KnowledgeGraphModelTest(TestCase):
    def test_create_graph(self):
        graph = KnowledgeGraphFactory(status="ready")
        self.assertEqual(graph.status, "ready")
        self.assertEqual(graph.entity_count, 0)

    def test_graph_one_to_one_with_kb(self):
        kb = KnowledgeBaseFactory()
        graph = KnowledgeGraphFactory(knowledge_base=kb)
        self.assertEqual(graph.knowledge_base, kb)
        with self.assertRaises(IntegrityError):
            KnowledgeGraphFactory(knowledge_base=kb)


# ─────────────────────────────────────────────────────
# RAGSkill
# ─────────────────────────────────────────────────────
class RAGSkillModelTest(TestCase):
    def test_create_skill(self):
        skill = RAGSkillFactory(name="Web Search", skill_type="builtin")
        self.assertEqual(skill.name, "Web Search")
        self.assertTrue(skill.is_active)

    def test_skill_slug_unique(self):
        RAGSkillFactory(slug="web-search")
        with self.assertRaises(IntegrityError):
            RAGSkillFactory(slug="web-search")


# ─────────────────────────────────────────────────────
# RAGConversation & RAGMessage
# ─────────────────────────────────────────────────────
class RAGConversationModelTest(TestCase):
    def test_create_conversation(self):
        conv = RAGConversationFactory(title="Test chat")
        self.assertEqual(conv.title, "Test chat")
        self.assertEqual(conv.message_count, 0)

    def test_conversation_belongs_to_user(self):
        user = UserFactory()
        conv = RAGConversationFactory(user=user)
        self.assertEqual(conv.user, user)


class RAGMessageModelTest(TestCase):
    def test_create_message(self):
        msg = RAGMessageFactory(role="user", content="Hello RAG")
        self.assertEqual(msg.role, "user")
        self.assertEqual(msg.content, "Hello RAG")

    def test_message_with_images(self):
        images = [{"id": "123", "url": "/img.png", "caption": "Test"}]
        msg = RAGMessageFactory(images=images)
        self.assertEqual(len(msg.images), 1)
        self.assertEqual(msg.images[0]["url"], "/img.png")

    def test_message_str_contains_role_and_content(self):
        msg = RAGMessageFactory(role="assistant", content="This is a test response.")
        s = str(msg)
        self.assertIn("assistant", s)
        self.assertIn("This is a test", s)


# ─────────────────────────────────────────────────────
# RAGAccessPermission
# ─────────────────────────────────────────────────────
class RAGAccessPermissionModelTest(TestCase):
    def test_create_permission(self):
        perm = RAGAccessPermissionFactory(access_level="use")
        self.assertEqual(perm.access_level, "use")
        self.assertEqual(perm.daily_query_limit, 100)

    def test_unique_together_instance_user(self):
        instance = RAGInstanceFactory()
        user = UserFactory()
        RAGAccessPermissionFactory(rag_instance=instance, user=user)
        with self.assertRaises(IntegrityError):
            RAGAccessPermissionFactory(rag_instance=instance, user=user)

    def test_str_contains_user_and_instance(self):
        s = str(RAGAccessPermissionFactory())
        self.assertIn("→", s)
