import factory
from factory.django import DjangoModelFactory

from apps.agents.tests.factories import AgentProviderFactory, AgentConfigFactory
from apps.graph_rag.models import (
    RAGInstance,
    RAGInstanceKnowledgeBase,
    KnowledgeBase,
    Document,
    DocumentChunk,
    KnowledgeGraph,
    GraphEntity,
    RAGSkill,
    RAGInstanceSkill,
    RAGConversation,
    RAGMessage,
    RAGAccessPermission,
    RAGUsageLog,
    RAGConfigHistory,
)
from apps.graph_rag.constants import DEFAULT_RETRIEVAL_CONFIG, DEFAULT_GENERATION_CONFIG


# ── Re-export user factories ───────────────────────
class UserFactory(DjangoModelFactory):
    class Meta:
        model = "users.User"
        django_get_or_create = ("email",)

    email = factory.Sequence(lambda n: f"raguser{n}@test.com")
    full_name = factory.Sequence(lambda n: f"RAG User {n}")
    is_active = True
    is_staff = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", "TestPass123!")
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, password=password, **kwargs)


class AdminUserFactory(UserFactory):
    is_staff = True
    is_superuser = True

    class Meta:
        model = "users.User"
        django_get_or_create = ("email",)


# ── RAG Instance ───────────────────────────────────
class RAGInstanceFactory(DjangoModelFactory):
    class Meta:
        model = RAGInstance

    name = factory.Sequence(lambda n: f"RAG Instance {n}")
    slug = factory.Sequence(lambda n: f"rag-instance-{n}")
    description = "Test RAG instance"
    purpose = "general"
    system_prompt = "You are a test assistant. Context: {context}"
    provider = factory.SubFactory(AgentProviderFactory)
    agent_config = factory.SubFactory(
        AgentConfigFactory, provider=factory.SelfAttribute("..provider")
    )
    retrieval_config = factory.LazyFunction(lambda: DEFAULT_RETRIEVAL_CONFIG.copy())
    generation_config = factory.LazyFunction(lambda: DEFAULT_GENERATION_CONFIG.copy())
    is_active = True
    is_public = False
    created_by = factory.SubFactory(AdminUserFactory)


# ── Knowledge Base ─────────────────────────────────
class KnowledgeBaseFactory(DjangoModelFactory):
    class Meta:
        model = KnowledgeBase

    name = factory.Sequence(lambda n: f"KB {n}")
    slug = factory.Sequence(lambda n: f"kb-{n}")
    description = "Test knowledge base"
    chunk_strategy = "recursive"
    chunk_size = 512
    chunk_overlap = 50
    embedding_model = "text-embedding-3-small"
    is_active = True
    created_by = factory.SubFactory(AdminUserFactory)


class DocumentFactory(DjangoModelFactory):
    class Meta:
        model = Document

    knowledge_base = factory.SubFactory(KnowledgeBaseFactory)
    title = factory.Sequence(lambda n: f"Document {n}")
    source_type = "text"
    content_text = "This is the content of the test document."
    is_image = False
    processing_status = "completed"


class ImageDocumentFactory(DocumentFactory):
    """Factory for image documents."""

    title = factory.Sequence(lambda n: f"Image {n}")
    source_type = "image_upload"
    content_text = ""
    is_image = True
    image_caption = "A test image showing a product diagram"
    image_tags = factory.LazyFunction(lambda: ["product", "diagram"])
    processing_status = "completed"


class DocumentChunkFactory(DjangoModelFactory):
    class Meta:
        model = DocumentChunk

    document = factory.SubFactory(DocumentFactory)
    content = factory.Sequence(lambda n: f"Chunk content number {n}")
    chunk_index = factory.Sequence(lambda n: n)
    token_count = 20
    is_image_chunk = False


class ImageChunkFactory(DocumentChunkFactory):
    """Factory for image caption chunks."""

    document = factory.SubFactory(ImageDocumentFactory)
    content = "[Image: Test] A test image showing a product diagram"
    is_image_chunk = True
    metadata = factory.LazyFunction(
        lambda: {"source": "image_caption", "image_url": "/media/test.png"}
    )


# ── Knowledge Graph ────────────────────────────────
class KnowledgeGraphFactory(DjangoModelFactory):
    class Meta:
        model = KnowledgeGraph

    knowledge_base = factory.SubFactory(KnowledgeBaseFactory)
    status = "ready"
    neo4j_graph_id = factory.LazyAttribute(lambda o: str(o.knowledge_base.id))


class GraphEntityFactory(DjangoModelFactory):
    class Meta:
        model = GraphEntity

    knowledge_graph = factory.SubFactory(KnowledgeGraphFactory)
    name = factory.Sequence(lambda n: f"Entity {n}")
    entity_type = "concept"
    description = "A test entity"


# ── Skill ──────────────────────────────────────────
class RAGSkillFactory(DjangoModelFactory):
    class Meta:
        model = RAGSkill

    name = factory.Sequence(lambda n: f"Skill {n}")
    slug = factory.Sequence(lambda n: f"skill-{n}")
    description = "Test skill"
    skill_type = "builtin"
    config = factory.LazyFunction(lambda: {"enabled": True})
    is_active = True


# ── Conversation ───────────────────────────────────
class RAGConversationFactory(DjangoModelFactory):
    class Meta:
        model = RAGConversation

    rag_instance = factory.SubFactory(RAGInstanceFactory)
    user = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: f"Conversation {n}")
    message_count = 0


class RAGMessageFactory(DjangoModelFactory):
    class Meta:
        model = RAGMessage

    conversation = factory.SubFactory(RAGConversationFactory)
    role = "assistant"
    content = "This is a test response."
    sources = factory.LazyFunction(list)
    images = factory.LazyFunction(list)


# ── Access ─────────────────────────────────────────
class RAGAccessPermissionFactory(DjangoModelFactory):
    class Meta:
        model = RAGAccessPermission

    rag_instance = factory.SubFactory(RAGInstanceFactory)
    user = factory.SubFactory(UserFactory)
    access_level = "use"
    daily_query_limit = 100
    monthly_token_limit = 1_000_000
    granted_by = factory.SubFactory(AdminUserFactory)


# ── Usage Log ──────────────────────────────────────
class RAGUsageLogFactory(DjangoModelFactory):
    class Meta:
        model = RAGUsageLog

    rag_instance = factory.SubFactory(RAGInstanceFactory)
    user = factory.SubFactory(UserFactory)
    query = "test query"
    retrieval_strategy = "hybrid"
    tokens_in = 50
    tokens_out = 100
    latency_ms = 200
    sources_count = 2


# ── Config History ─────────────────────────────────
class RAGConfigHistoryFactory(DjangoModelFactory):
    class Meta:
        model = RAGConfigHistory

    rag_instance = factory.SubFactory(RAGInstanceFactory)
    config_type = "retrieval"
    old_value = factory.LazyFunction(lambda: {"top_k_vector": 10})
    new_value = factory.LazyFunction(lambda: {"top_k_vector": 20})
    changed_by = factory.SubFactory(AdminUserFactory)
    reason = "Test config change"


# ── Analytics ──────────────────────────────────────
class RAGUsageLogFactory(DjangoModelFactory):
    class Meta:
        model = RAGUsageLog

    rag_instance = factory.SubFactory(RAGInstanceFactory)
    user = factory.SubFactory(UserFactory)
    query = "test query"
    retrieval_strategy = "hybrid"
    latency_ms = 200
    sources_count = 3
    images_returned = 0


class RAGConfigHistoryFactory(DjangoModelFactory):
    class Meta:
        model = RAGConfigHistory

    rag_instance = factory.SubFactory(RAGInstanceFactory)
    config_type = "retrieval"
    old_value = factory.LazyFunction(lambda: {"top_k_final": 5})
    new_value = factory.LazyFunction(lambda: {"top_k_final": 10})
    changed_by = factory.SubFactory(AdminUserFactory)
    reason = "Testing config change"
