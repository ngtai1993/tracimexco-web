# GraphRAG — Kiến Trúc Chi Tiết

---

## 1. Django App Structure

```
backend/apps/graph_rag/
├── __init__.py
├── apps.py
├── urls.py
├── admin.py
├── exceptions.py
├── constants.py
├── signals.py
│
├── models/
│   ├── __init__.py
│   ├── rag_instance.py           # RAGInstance, RAGInstanceKnowledgeBase
│   ├── knowledge_base.py         # KnowledgeBase, Document, DocumentChunk
│   ├── knowledge_graph.py        # KnowledgeGraph, GraphEntity, GraphRelationship, GraphCommunity
│   ├── skill.py                  # RAGSkill, RAGInstanceSkill
│   ├── conversation.py           # RAGConversation, RAGMessage
│   ├── access.py                 # RAGAccessPermission, RAGUsageQuota
│   └── analytics.py              # RAGUsageLog, RAGConfigHistory
│
├── services/
│   ├── __init__.py
│   ├── rag_instance_service.py   # CRUD + clone RAG instances
│   ├── knowledge_base_service.py # CRUD KB + documents
│   ├── document_processor.py     # Chunking, embedding, processing pipeline
│   ├── graph_builder_service.py  # Extract entities/relations, build graph
│   ├── community_service.py      # Community detection + summarization
│   ├── retrieval_service.py      # Vector search, graph search, hybrid
│   ├── pipeline_service.py       # Full RAG pipeline orchestration
│   ├── generation_service.py     # LLM call + streaming
│   ├── skill_service.py          # Skill registry + execution
│   ├── conversation_service.py   # Chat history management
│   ├── access_service.py         # Permission + quota management
│   └── analytics_service.py      # Usage logging + stats
│
├── selectors/
│   ├── __init__.py
│   ├── rag_instance_selector.py
│   ├── knowledge_base_selector.py
│   ├── graph_selector.py
│   ├── conversation_selector.py
│   ├── skill_selector.py
│   └── analytics_selector.py
│
├── serializers/
│   ├── __init__.py
│   ├── rag_instance_serializer.py
│   ├── knowledge_base_serializer.py
│   ├── document_serializer.py
│   ├── graph_serializer.py
│   ├── skill_serializer.py
│   ├── conversation_serializer.py
│   ├── chat_serializer.py
│   ├── access_serializer.py
│   └── analytics_serializer.py
│
├── views/
│   ├── __init__.py
│   ├── rag_instance_views.py
│   ├── knowledge_base_views.py
│   ├── document_views.py
│   ├── graph_views.py
│   ├── skill_views.py
│   ├── chat_views.py
│   ├── conversation_views.py
│   ├── access_views.py
│   └── analytics_views.py
│
├── pipeline/                      # RAG Pipeline components
│   ├── __init__.py
│   ├── query_analyzer.py          # Phân tích query, detect intent
│   ├── query_decomposer.py        # Chia query thành sub-queries
│   ├── vector_retriever.py        # pgvector search
│   ├── graph_retriever.py         # Neo4j traversal
│   ├── keyword_retriever.py       # Full-text search
│   ├── reranker.py                # Cross-encoder reranking
│   ├── context_builder.py         # Assemble context from results
│   ├── generator.py               # LLM generation
│   ├── verifier.py                # Self-verification
│   └── skill_executor.py          # Execute skills/tools
│
├── skills/                        # Built-in skills
│   ├── __init__.py
│   ├── base_skill.py              # Abstract base class
│   ├── web_search.py              # Web search skill
│   ├── calculator.py              # Math computation
│   ├── summarizer.py              # Text summarization
│   ├── translator.py              # Translation
│   └── content_generator.py       # Structured content generation
│
├── graph/                         # Knowledge Graph operations
│   ├── __init__.py
│   ├── neo4j_client.py            # Neo4j connection manager
│   ├── entity_extractor.py        # LLM-based entity extraction
│   ├── relation_extractor.py      # LLM-based relation extraction
│   ├── community_detector.py      # Leiden/Louvain algorithm
│   └── graph_queries.py           # Common Cypher queries
│
├── migrations/
│
└── tests/
    ├── __init__.py
    ├── test_rag_instance_service.py
    ├── test_document_processor.py
    ├── test_retrieval_service.py
    ├── test_pipeline_service.py
    ├── test_graph_builder.py
    ├── test_skills.py
    └── test_api/
        ├── test_rag_instance_api.py
        ├── test_knowledge_base_api.py
        ├── test_chat_api.py
        └── test_access_api.py
```

---

## 2. Models Chi Tiết

### 2.1 RAGInstance — Con RAG chính

```python
class RAGInstance(BaseModel):
    """
    Mỗi instance là một 'con RAG' riêng biệt, phục vụ một mục đích cụ thể.
    Admin tạo và cấu hình, Manager/User được cấp quyền sử dụng.
    """
    id = UUIDField(primary_key=True, default=uuid4)
    name = CharField(max_length=200)
    slug = SlugField(unique=True)
    description = TextField(blank=True)

    # Mục đích sử dụng
    PURPOSE_CHOICES = [
        ('customer_support', 'Hỗ trợ khách hàng'),
        ('content_creation', 'Tạo nội dung'),
        ('code_assistant', 'Trợ lý code'),
        ('data_analysis', 'Phân tích dữ liệu'),
        ('education', 'Giáo dục & đào tạo'),
        ('internal_qa', 'Q&A nội bộ'),
        ('general', 'Đa mục đích'),
        ('custom', 'Tùy chỉnh'),
    ]
    purpose = CharField(max_length=50, choices=PURPOSE_CHOICES, default='general')

    # System prompt — chỉ dẫn cho LLM
    system_prompt = TextField(
        help_text="Template system prompt. Hỗ trợ variables: {context}, {sources}, {language}"
    )

    # AI Provider & Model (từ app agents)
    provider = ForeignKey('agents.AgentProvider', on_delete=PROTECT)
    agent_config = ForeignKey('agents.AgentConfig', on_delete=SET_NULL, null=True, blank=True)

    # Configurable parameters (JSON fields, tinh chỉnh qua API)
    retrieval_config = JSONField(default=dict, help_text="Retrieval parameters")
    generation_config = JSONField(default=dict, help_text="Generation parameters")

    # Status
    is_active = BooleanField(default=True)
    is_public = BooleanField(default=False, help_text="Tất cả user đều dùng được")

    # Ownership
    created_by = ForeignKey('users.User', on_delete=SET_NULL, null=True)

    class Meta:
        ordering = ['-created_at']
```

### 2.2 RAGInstanceKnowledgeBase — Gán KB cho Instance

```python
class RAGInstanceKnowledgeBase(BaseModel):
    """Gán Knowledge Base cho RAG Instance với priority."""
    rag_instance = ForeignKey(RAGInstance, on_delete=CASCADE, related_name='knowledge_bases')
    knowledge_base = ForeignKey('KnowledgeBase', on_delete=CASCADE)
    priority = PositiveIntegerField(default=1, help_text="1 = cao nhất")

    class Meta:
        unique_together = ['rag_instance', 'knowledge_base']
        ordering = ['priority']
```

### 2.3 KnowledgeBase — Bộ tài liệu

```python
class KnowledgeBase(BaseModel):
    """Bộ tài liệu nguồn cho RAG."""
    id = UUIDField(primary_key=True, default=uuid4)
    name = CharField(max_length=200)
    slug = SlugField(unique=True)
    description = TextField(blank=True)

    # Chunking configuration
    CHUNK_STRATEGY_CHOICES = [
        ('fixed', 'Fixed Size'),
        ('recursive', 'Recursive Character'),
        ('semantic', 'Semantic Chunking'),
    ]
    chunk_strategy = CharField(max_length=20, choices=CHUNK_STRATEGY_CHOICES, default='recursive')
    chunk_size = PositiveIntegerField(default=512)
    chunk_overlap = PositiveIntegerField(default=50)

    # Embedding
    embedding_model = CharField(max_length=100, default='text-embedding-3-small')
    embedding_dimensions = PositiveIntegerField(default=1536)

    # Stats (denormalized for performance)
    document_count = PositiveIntegerField(default=0)
    total_chunks = PositiveIntegerField(default=0)

    is_active = BooleanField(default=True)
    created_by = ForeignKey('users.User', on_delete=SET_NULL, null=True)

    class Meta:
        ordering = ['-created_at']
```

### 2.4 Document — Tài liệu đơn lẻ

```python
class Document(BaseModel):
    """Một tài liệu trong Knowledge Base."""
    id = UUIDField(primary_key=True, default=uuid4)
    knowledge_base = ForeignKey(KnowledgeBase, on_delete=CASCADE, related_name='documents')

    title = CharField(max_length=500)
    description = TextField(blank=True)

    # Source
    SOURCE_TYPE_CHOICES = [
        ('file_upload', 'File Upload'),
        ('url', 'URL Import'),
        ('text', 'Plain Text'),
        ('api', 'API Import'),
    ]
    source_type = CharField(max_length=20, choices=SOURCE_TYPE_CHOICES)
    source_url = URLField(blank=True, null=True)
    file = FileField(upload_to='graph_rag/documents/', blank=True, null=True)
    content_text = TextField(blank=True, help_text="Extracted raw text")

    # Processing status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('chunking', 'Chunking'),
        ('embedding', 'Embedding'),
        ('extracting_entities', 'Extracting Entities'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    processing_status = CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    processing_error = TextField(blank=True)
    processed_at = DateTimeField(null=True)

    # Stats
    chunk_count = PositiveIntegerField(default=0)
    entity_count = PositiveIntegerField(default=0)
    token_count = PositiveIntegerField(default=0)

    # Metadata
    metadata = JSONField(default=dict, help_text="File size, page count, language, etc.")

    class Meta:
        ordering = ['-created_at']
```

### 2.5 DocumentChunk — Chunks

```python
class DocumentChunk(BaseModel):
    """Một chunk của document, đã được embed."""
    id = UUIDField(primary_key=True, default=uuid4)
    document = ForeignKey(Document, on_delete=CASCADE, related_name='chunks')

    content = TextField()
    chunk_index = PositiveIntegerField()

    # Vector embedding (pgvector)
    embedding = VectorField(dimensions=1536, null=True)

    # Metadata
    metadata = JSONField(default=dict, help_text="page_number, start_char, end_char, etc.")
    token_count = PositiveIntegerField(default=0)

    class Meta:
        ordering = ['document', 'chunk_index']
        indexes = [
            # pgvector index for similarity search
            # IVFFlat or HNSW index
        ]
```

### 2.6 KnowledgeGraph — Metadata graph

```python
class KnowledgeGraph(BaseModel):
    """Metadata cho Knowledge Graph của một Knowledge Base."""
    id = UUIDField(primary_key=True, default=uuid4)
    knowledge_base = OneToOneField(KnowledgeBase, on_delete=CASCADE, related_name='graph')

    STATUS_CHOICES = [
        ('not_built', 'Not Built'),
        ('building', 'Building'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
        ('rebuilding', 'Rebuilding'),
    ]
    status = CharField(max_length=20, choices=STATUS_CHOICES, default='not_built')

    # Stats
    entity_count = PositiveIntegerField(default=0)
    relationship_count = PositiveIntegerField(default=0)
    community_count = PositiveIntegerField(default=0)

    last_built_at = DateTimeField(null=True)
    build_error = TextField(blank=True)

    # Neo4j reference
    neo4j_graph_id = CharField(max_length=100, blank=True,
        help_text="Identifier trong Neo4j để isolate data per KB")
```

### 2.7 GraphEntity — Thực thể trong graph

```python
class GraphEntity(BaseModel):
    """Một entity được extract từ documents."""
    id = UUIDField(primary_key=True, default=uuid4)
    knowledge_graph = ForeignKey(KnowledgeGraph, on_delete=CASCADE, related_name='entities')

    name = CharField(max_length=500)
    ENTITY_TYPE_CHOICES = [
        ('person', 'Person'),
        ('organization', 'Organization'),
        ('location', 'Location'),
        ('concept', 'Concept'),
        ('event', 'Event'),
        ('product', 'Product'),
        ('technology', 'Technology'),
        ('document', 'Document'),
        ('other', 'Other'),
    ]
    entity_type = CharField(max_length=50, choices=ENTITY_TYPE_CHOICES)
    description = TextField(blank=True)
    properties = JSONField(default=dict)

    # Source chunks mà entity được extract từ đó
    source_chunks = ManyToManyField(DocumentChunk, blank=True, related_name='entities')

    # Neo4j node ID (để sync)
    neo4j_node_id = CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['name']
        unique_together = ['knowledge_graph', 'name', 'entity_type']
```

### 2.8 GraphRelationship — Quan hệ

```python
class GraphRelationship(BaseModel):
    """Quan hệ giữa hai entities."""
    id = UUIDField(primary_key=True, default=uuid4)
    knowledge_graph = ForeignKey(KnowledgeGraph, on_delete=CASCADE, related_name='relationships')

    source_entity = ForeignKey(GraphEntity, on_delete=CASCADE, related_name='outgoing_relations')
    target_entity = ForeignKey(GraphEntity, on_delete=CASCADE, related_name='incoming_relations')

    relationship_type = CharField(max_length=200)  # "works_at", "located_in", "related_to"
    description = TextField(blank=True)
    weight = FloatField(default=1.0, help_text="Confidence/strength score 0-1")
    properties = JSONField(default=dict)

    # Source chunks
    source_chunks = ManyToManyField(DocumentChunk, blank=True, related_name='relationships')

    # Neo4j relationship ID
    neo4j_rel_id = CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-weight']
```

### 2.9 GraphCommunity — Cộng đồng entities

```python
class GraphCommunity(BaseModel):
    """Một community of related entities, với LLM-generated summary."""
    id = UUIDField(primary_key=True, default=uuid4)
    knowledge_graph = ForeignKey(KnowledgeGraph, on_delete=CASCADE, related_name='communities')

    level = PositiveIntegerField(help_text="Hierarchy level (0 = most granular)")
    title = CharField(max_length=500)
    summary = TextField(help_text="LLM-generated summary of this community")
    rank = FloatField(default=0.0, help_text="Importance score")

    # Entities in this community
    entities = ManyToManyField(GraphEntity, blank=True, related_name='communities')

    class Meta:
        ordering = ['level', '-rank']
```

### 2.10 RAGSkill — Skills/Tools

```python
class RAGSkill(BaseModel):
    """Một skill/tool mà RAG instance có thể sử dụng."""
    id = UUIDField(primary_key=True, default=uuid4)
    name = CharField(max_length=200)
    slug = SlugField(unique=True)
    description = TextField(help_text="Mô tả cho LLM biết khi nào dùng skill này")

    SKILL_TYPE_CHOICES = [
        ('builtin', 'Built-in'),
        ('api_call', 'External API Call'),
        ('custom', 'Custom Implementation'),
    ]
    skill_type = CharField(max_length=20, choices=SKILL_TYPE_CHOICES)

    # Configuration
    config = JSONField(default=dict, help_text="Skill-specific config")
    input_schema = JSONField(default=dict, help_text="JSON Schema for input")
    output_schema = JSONField(default=dict, help_text="JSON Schema for output")

    # Implementation
    implementation_path = CharField(
        max_length=500, blank=True,
        help_text="Python path to skill class, e.g., 'apps.graph_rag.skills.web_search.WebSearchSkill'"
    )
    api_endpoint = URLField(blank=True, null=True, help_text="For api_call type")
    api_method = CharField(max_length=10, default='POST')
    api_headers = JSONField(default=dict, blank=True)

    is_active = BooleanField(default=True)
    created_by = ForeignKey('users.User', on_delete=SET_NULL, null=True)

    class Meta:
        ordering = ['name']
```

### 2.11 RAGInstanceSkill — Gán skill cho instance

```python
class RAGInstanceSkill(BaseModel):
    """Gán skill cho RAG instance với config override."""
    rag_instance = ForeignKey(RAGInstance, on_delete=CASCADE, related_name='skills')
    skill = ForeignKey(RAGSkill, on_delete=CASCADE)
    is_enabled = BooleanField(default=True)
    config_override = JSONField(default=dict, help_text="Override skill config per instance")

    class Meta:
        unique_together = ['rag_instance', 'skill']
```

### 2.12 RAGConversation & RAGMessage — Chat

```python
class RAGConversation(BaseModel):
    """Một phiên chat với RAG instance."""
    id = UUIDField(primary_key=True, default=uuid4)
    rag_instance = ForeignKey(RAGInstance, on_delete=CASCADE, related_name='conversations')
    user = ForeignKey('users.User', on_delete=CASCADE, related_name='rag_conversations')
    title = CharField(max_length=500, blank=True)
    is_active = BooleanField(default=True)
    message_count = PositiveIntegerField(default=0)
    metadata = JSONField(default=dict)

    class Meta:
        ordering = ['-updated_at']


class RAGMessage(BaseModel):
    """Một tin nhắn trong conversation."""
    id = UUIDField(primary_key=True, default=uuid4)
    conversation = ForeignKey(RAGConversation, on_delete=CASCADE, related_name='messages')

    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    role = CharField(max_length=20, choices=ROLE_CHOICES)
    content = TextField()

    # Sources used for this response
    sources = JSONField(default=list, help_text="""
        [{"type": "chunk", "id": "uuid", "content": "...", "document": "...", "score": 0.95},
         {"type": "entity", "id": "uuid", "name": "...", "type": "person"},
         {"type": "community", "id": "uuid", "summary": "..."}]
    """)

    # Skills used
    skills_used = JSONField(default=list, help_text="""
        [{"skill": "web_search", "query": "...", "result_summary": "..."}]
    """)

    # Metadata
    metadata = JSONField(default=dict, help_text="""
        {"tokens_in": 1500, "tokens_out": 500, "latency_ms": 2300,
         "retrieval_strategy": "hybrid", "model": "gpt-4o",
         "sub_queries": ["query1", "query2"]}
    """)

    # Feedback
    FEEDBACK_CHOICES = [
        ('thumbs_up', '👍'),
        ('thumbs_down', '👎'),
    ]
    feedback = CharField(max_length=20, choices=FEEDBACK_CHOICES, null=True, blank=True)
    feedback_comment = TextField(blank=True)

    class Meta:
        ordering = ['created_at']
```

### 2.13 RAGAccessPermission — Quyền truy cập

```python
class RAGAccessPermission(BaseModel):
    """Quyền sử dụng RAG instance."""
    id = UUIDField(primary_key=True, default=uuid4)
    rag_instance = ForeignKey(RAGInstance, on_delete=CASCADE, related_name='permissions')
    user = ForeignKey('users.User', on_delete=CASCADE, related_name='rag_permissions')

    ACCESS_LEVEL_CHOICES = [
        ('use', 'Sử dụng (chat only)'),
        ('use_upload', 'Sử dụng + Upload docs'),
        ('view_analytics', 'Xem analytics'),
        ('full', 'Full access (trừ config)'),
    ]
    access_level = CharField(max_length=20, choices=ACCESS_LEVEL_CHOICES, default='use')

    # Quota
    daily_query_limit = PositiveIntegerField(default=100)
    monthly_token_limit = PositiveIntegerField(default=1_000_000)

    granted_by = ForeignKey('users.User', on_delete=SET_NULL, null=True, related_name='granted_rag_permissions')
    expires_at = DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['rag_instance', 'user']
```

### 2.14 RAGUsageLog — Usage tracking

```python
class RAGUsageLog(BaseModel):
    """Log mỗi query để tracking và analytics."""
    id = UUIDField(primary_key=True, default=uuid4)
    rag_instance = ForeignKey(RAGInstance, on_delete=CASCADE, related_name='usage_logs')
    user = ForeignKey('users.User', on_delete=SET_NULL, null=True)
    conversation = ForeignKey(RAGConversation, on_delete=SET_NULL, null=True)

    query = TextField()
    retrieval_strategy = CharField(max_length=20)
    tokens_in = PositiveIntegerField(default=0)
    tokens_out = PositiveIntegerField(default=0)
    latency_ms = PositiveIntegerField(default=0)

    # Quality
    sources_count = PositiveIntegerField(default=0)
    skills_used = JSONField(default=list)
    feedback = CharField(max_length=20, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            Index(fields=['rag_instance', 'created_at']),
            Index(fields=['user', 'created_at']),
        ]
```

### 2.15 RAGConfigHistory — Config change log

```python
class RAGConfigHistory(BaseModel):
    """Log mỗi lần thay đổi config của RAG instance."""
    id = UUIDField(primary_key=True, default=uuid4)
    rag_instance = ForeignKey(RAGInstance, on_delete=CASCADE, related_name='config_history')

    CONFIG_TYPE_CHOICES = [
        ('retrieval', 'Retrieval Config'),
        ('generation', 'Generation Config'),
        ('system_prompt', 'System Prompt'),
    ]
    config_type = CharField(max_length=20, choices=CONFIG_TYPE_CHOICES)

    old_value = JSONField()
    new_value = JSONField()
    changed_by = ForeignKey('users.User', on_delete=SET_NULL, null=True)
    reason = TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
```

---

## 3. Services Chi Tiết

### 3.1 RAGInstanceService

```python
class RAGInstanceService:
    """Quản lý CRUD cho RAG instances."""

    @staticmethod
    def create(*, name, slug, description, purpose, system_prompt,
               provider_id, agent_config_id=None, retrieval_config=None,
               generation_config=None, created_by) -> RAGInstance:
        """Tạo RAG instance mới với default config."""
        retrieval_config = {**DEFAULT_RETRIEVAL_CONFIG, **(retrieval_config or {})}
        generation_config = {**DEFAULT_GENERATION_CONFIG, **(generation_config or {})}
        # ...

    @staticmethod
    def update_config(*, instance_id, config_type, new_config, changed_by, reason=""):
        """Update config và log history."""
        # Save old config to RAGConfigHistory
        # Merge new config with existing
        # ...

    @staticmethod
    def clone(*, source_id, new_name, new_slug, created_by) -> RAGInstance:
        """Clone RAG instance (copy config, KB assignments, skills)."""
        # ...

    @staticmethod
    def assign_knowledge_base(*, instance_id, kb_id, priority=1):
        """Gán Knowledge Base cho instance."""
        # ...

    @staticmethod
    def assign_skill(*, instance_id, skill_id, config_override=None):
        """Gán skill cho instance."""
        # ...
```

### 3.2 DocumentProcessorService

```python
class DocumentProcessorService:
    """Pipeline xử lý document: parse → chunk → embed → extract entities."""

    @staticmethod
    def process_document(document_id: str):
        """Celery task: Full processing pipeline cho 1 document."""
        # 1. Parse document (unstructured)
        # 2. Extract text
        # 3. Chunk text (theo KB config)
        # 4. Generate embeddings (via agent API key)
        # 5. Store chunks + embeddings (pgvector)
        # 6. Extract entities & relationships (LLM)
        # 7. Store in Knowledge Graph (Neo4j)
        # 8. Update document status & stats

    @staticmethod
    def chunk_text(text: str, strategy: str, chunk_size: int, overlap: int) -> list[str]:
        """Chunk text theo chiến lược."""
        # fixed: chia đều theo chunk_size
        # recursive: RecursiveCharacterTextSplitter (LangChain)
        # semantic: SemanticChunker (LangChain)

    @staticmethod
    def generate_embeddings(chunks: list[str], model: str, api_key: str) -> list[list[float]]:
        """Generate embeddings cho list of chunks."""
        # Dùng OpenAI embeddings API hoặc local model
```

### 3.3 GraphBuilderService

```python
class GraphBuilderService:
    """Xây dựng Knowledge Graph từ documents."""

    @staticmethod
    def extract_entities(text: str, api_key: str, model: str) -> list[dict]:
        """
        Dùng LLM để extract entities từ text.
        Returns: [{"name": "...", "type": "person", "description": "..."}]
        """
        # Prompt LLM to extract named entities
        # Use structured output (JSON mode)

    @staticmethod
    def extract_relationships(text: str, entities: list[dict], api_key: str, model: str) -> list[dict]:
        """
        Dùng LLM để extract relationships giữa entities.
        Returns: [{"source": "A", "target": "B", "type": "works_at", "description": "..."}]
        """

    @staticmethod
    def build_graph(knowledge_base_id: str):
        """Celery task: Build toàn bộ knowledge graph cho 1 KB."""
        # 1. Lấy tất cả chunks
        # 2. Extract entities từ mỗi chunk batch
        # 3. Deduplicate entities
        # 4. Extract relationships
        # 5. Store in Neo4j + Django models
        # 6. Run community detection
        # 7. Generate community summaries

    @staticmethod
    def rebuild_graph(knowledge_base_id: str):
        """Xóa graph cũ và build lại."""
```

### 3.4 CommunityService

```python
class CommunityService:
    """Community detection và summarization."""

    @staticmethod
    def detect_communities(knowledge_graph_id: str, algorithm='leiden') -> list:
        """
        Detect communities bằng Leiden/Louvain algorithm.
        Returns hierarchical communities.
        """
        # 1. Load graph from Neo4j vào NetworkX
        # 2. Run community detection (cdlib)
        # 3. Generate multi-level hierarchy
        # 4. Store communities in DB + Neo4j

    @staticmethod
    def summarize_community(community_id: str, api_key: str, model: str) -> str:
        """Dùng LLM để tạo summary cho 1 community."""
        # Lấy tất cả entities + relationships trong community
        # Prompt LLM: "Summarize the following group of entities and their relationships..."
```

### 3.5 RetrievalService

```python
class RetrievalService:
    """Multi-strategy retrieval engine."""

    @staticmethod
    def vector_search(query_embedding: list[float], kb_ids: list[str],
                      top_k: int, threshold: float) -> list[dict]:
        """pgvector cosine similarity search."""
        # SELECT * FROM document_chunks
        # ORDER BY embedding <=> query_embedding
        # LIMIT top_k
        # WHERE similarity > threshold

    @staticmethod
    def graph_search(query: str, entities: list[str], kb_ids: list[str],
                     depth: int, top_k: int) -> list[dict]:
        """
        Neo4j graph traversal:
        1. Tìm entities matching query
        2. Traverse relationships (depth N)
        3. Return connected entities + their source chunks
        """

    @staticmethod
    def community_search(query: str, kb_ids: list[str],
                         level: int, top_k: int) -> list[dict]:
        """Tìm community summaries phù hợp nhất."""
        # Embed query → similarity search trên community summaries

    @staticmethod
    def keyword_search(query: str, kb_ids: list[str], top_k: int) -> list[dict]:
        """Full-text search trên PostgreSQL."""
        # Django SearchVector / SearchQuery

    @staticmethod
    def hybrid_search(query: str, query_embedding: list[float],
                      kb_ids: list[str], config: dict) -> list[dict]:
        """
        Kết hợp tất cả strategies:
        1. Vector search → top_k_vector results
        2. Graph search → top_k_graph results
        3. Community search → top communities
        4. Keyword search → top_k results
        5. Merge + deduplicate
        6. Rerank → top_k_final results
        """

    @staticmethod
    def rerank(query: str, results: list[dict], top_k: int,
               model: str = 'cross-encoder/ms-marco-MiniLM-L-6-v2') -> list[dict]:
        """Cross-encoder reranking cho kết quả chính xác hơn."""
```

### 3.6 PipelineService — Orchestra

```python
class PipelineService:
    """Điều phối toàn bộ RAG pipeline từ query → response."""

    @staticmethod
    def process_query(*, rag_instance_id: str, query: str, conversation_id: str = None,
                      user_id: str) -> dict:
        """
        Full pipeline:
        1. Load RAG instance + config
        2. Check permissions & quota
        3. Analyze query (intent, complexity)
        4. Decompose if needed
        5. For each (sub-)query:
           a. Generate embedding
           b. Retrieve (vector + graph + community)
           c. Rerank
        6. Build context
        7. Check if skills needed
        8. Execute skills
        9. Generate response (LLM)
        10. Self-verify (optional)
        11. Save message + log usage
        12. Return response with sources

        Returns:
        {
            "answer": "...",
            "sources": [...],
            "skills_used": [...],
            "metadata": {"tokens_in": ..., "tokens_out": ..., "latency_ms": ...}
        }
        """

    @staticmethod
    def process_query_stream(*, rag_instance_id, query, conversation_id=None, user_id):
        """Same as process_query but yields chunks for SSE streaming."""
        # yield {"type": "retrieval", "data": {"strategy": "hybrid", "results_count": 15}}
        # yield {"type": "thinking", "data": {"step": "reranking"}}
        # yield {"type": "token", "data": {"content": "Theo"}}
        # yield {"type": "token", "data": {"content": " tài liệu..."}}
        # yield {"type": "sources", "data": [{"type": "chunk", ...}]}
        # yield {"type": "done", "data": {"metadata": {...}}}
```

### 3.7 SkillService

```python
class SkillService:
    """Registry và execution cho skills."""

    @staticmethod
    def get_available_skills(rag_instance_id: str) -> list[dict]:
        """Lấy danh sách skills enabled cho instance."""
        # Return: [{"name": "web_search", "description": "...", "input_schema": {...}}]

    @staticmethod
    def should_use_skills(query: str, context: str, available_skills: list) -> list[dict]:
        """
        Dùng LLM function calling để xác định skills cần thiết.
        Returns: [{"skill": "web_search", "input": {"query": "latest news about..."}}]
        """

    @staticmethod
    def execute_skill(skill_slug: str, input_data: dict, config: dict) -> dict:
        """Execute một skill và return kết quả."""
        # 1. Load skill class (builtin) hoặc call API (api_call)
        # 2. Validate input
        # 3. Execute
        # 4. Return result
```

---

## 4. RAG Pipeline Flow Chi Tiết

```
User sends query
       │
       ▼
┌──────────────────┐
│ 1. QUERY ANALYSIS │
│ ─ Detect intent   │    Intent types:
│ ─ Extract entities │    - factual: "X là gì?"
│ ─ Assess complexity│    - analytical: "So sánh A và B"
│ ─ Detect language  │    - creative: "Viết bài về..."
└────────┬─────────┘    - navigational: "Tìm doc về..."
         │
         ▼
┌──────────────────┐
│ 2. DECOMPOSITION  │    Complex query:
│ (if complex)      │    "So sánh chính sách A và B, ưu nhược điểm"
│                   │    → Sub-query 1: "Chính sách A là gì?"
│                   │    → Sub-query 2: "Chính sách B là gì?"
│                   │    → Sub-query 3: "Ưu nhược điểm A"
│                   │    → Sub-query 4: "Ưu nhược điểm B"
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 3. STRATEGY       │    Based on intent:
│ SELECTION         │    - factual → vector + graph
│ (adaptive)        │    - analytical → graph + community
│                   │    - creative → community + skills
│                   │    - navigational → keyword + vector
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 4. RETRIEVAL      │
│ ┌──────────────┐ │
│ │ Vector Search│──│──→ top_k chunks by similarity
│ └──────────────┘ │
│ ┌──────────────┐ │
│ │ Graph Search │──│──→ related entities + their chunks
│ └──────────────┘ │
│ ┌──────────────┐ │
│ │ Community    │──│──→ relevant community summaries
│ │ Search       │ │
│ └──────────────┘ │
│ ┌──────────────┐ │
│ │ Keyword      │──│──→ exact match results
│ │ Search       │ │
│ └──────────────┘ │
└────────┬─────────┘
         │ Merge all results
         ▼
┌──────────────────┐
│ 5. RERANKING      │    Cross-encoder scores:
│ Merge + Dedupe    │    chunk_A: 0.95
│ Cross-encoder     │    chunk_B: 0.91
│ → top_k_final     │    entity_X: 0.88
└────────┬─────────┘    community_Y: 0.85
         │
         ▼
┌──────────────────┐
│ 6. CONTEXT BUILD  │    Assemble:
│ ─ Ranked chunks   │    - Top chunks (with source info)
│ ─ Entity info     │    - Related entities + descriptions
│ ─ Community sums  │    - Community summaries
│ ─ Conversation    │    - Previous messages (if any)
│   history         │    - Skills results (if any)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 7. SKILL CHECK    │    LLM decides if tools needed:
│ (function calling)│    - "Need current data" → web_search
│                   │    - "Need calculation" → calculator
│                   │    - "Need translation" → translator
│                   │    If skills used → add results to context
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 8. GENERATION     │    System prompt + Context + Query
│ ─ LLM call       │    → LLM generates answer
│ ─ Stream tokens   │    → With source citations
│ ─ Format response │    → In configured format/language/tone
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 9. VERIFICATION   │    LLM self-check:
│ (optional)        │    - Answer consistent with context?
│                   │    - Any hallucination detected?
│                   │    - Sources properly cited?
│                   │    If failed → regenerate with feedback
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 10. RESPONSE      │
│ ─ Save message    │    {
│ ─ Log usage       │      "answer": "...",
│ ─ Return          │      "sources": [...],
│                   │      "skills_used": [...],
│                   │      "metadata": {...}
│                   │    }
└──────────────────┘
```

---

## 5. Neo4j Schema

```cypher
// Entity nodes
(:Entity {
    id: "uuid",
    name: "Microsoft",
    entity_type: "organization",
    description: "...",
    knowledge_base_id: "uuid",
    properties: {} // JSON
})

// Relationships
(:Entity)-[:RELATIONSHIP {
    id: "uuid",
    type: "founded_by",
    description: "...",
    weight: 0.95,
    properties: {}
}]->(:Entity)

// Community membership
(:Entity)-[:BELONGS_TO {level: 0}]->(:Community {
    id: "uuid",
    level: 0,
    title: "...",
    summary: "...",
    rank: 0.85,
    knowledge_base_id: "uuid"
})

// Entity → Source Chunk reference
(:Entity)-[:EXTRACTED_FROM]->(:ChunkRef {
    chunk_id: "uuid",
    document_id: "uuid",
    document_title: "..."
})

// Indexes
CREATE INDEX entity_name FOR (e:Entity) ON (e.name);
CREATE INDEX entity_kb FOR (e:Entity) ON (e.knowledge_base_id);
CREATE INDEX community_kb FOR (c:Community) ON (c.knowledge_base_id);
```

---

## 6. Celery Tasks

```python
# tasks/graph_rag_tasks.py

@shared_task(bind=True, max_retries=3)
def process_document_task(self, document_id: str):
    """Async document processing: parse → chunk → embed."""

@shared_task(bind=True, max_retries=2)
def build_knowledge_graph_task(self, knowledge_base_id: str):
    """Async graph building: extract entities → relationships → communities."""

@shared_task
def summarize_communities_task(knowledge_graph_id: str):
    """Generate LLM summaries for all communities."""

@shared_task
def log_rag_usage_task(usage_data: dict):
    """Non-blocking usage logging."""

@shared_task
def rebuild_graph_task(knowledge_base_id: str):
    """Rebuild graph khi documents thay đổi."""

# Periodic tasks
@shared_task
def cleanup_expired_permissions():
    """Xóa permissions hết hạn."""

@shared_task
def aggregate_daily_analytics():
    """Tổng hợp analytics hàng ngày."""
```

---

## 7. Settings Cần Thêm

```python
# config/settings/base.py

# GraphRAG
GRAPH_RAG_DEFAULT_RETRIEVAL_CONFIG = {
    "search_strategy": "hybrid",
    "top_k_vector": 10,
    "top_k_graph": 5,
    "top_k_final": 5,
    "similarity_threshold": 0.7,
    "graph_depth": 2,
    "community_level": 1,
    "reranking_enabled": True,
    "query_decomposition": True,
    "max_sub_queries": 3,
    "self_verification": False,
    "embedding_model": "text-embedding-3-small",
}

GRAPH_RAG_DEFAULT_GENERATION_CONFIG = {
    "temperature": 0.7,
    "max_tokens": 2048,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "response_format": "markdown",
    "language": "vi",
    "tone": "professional",
    "include_sources": True,
    "max_context_tokens": 4096,
    "stream": True,
}

GRAPH_RAG_DEFAULT_KB_CONFIG = {
    "chunk_strategy": "recursive",
    "chunk_size": 512,
    "chunk_overlap": 50,
    "embedding_model": "text-embedding-3-small",
}

# Neo4j
NEO4J_URI = config("NEO4J_URI", default="bolt://localhost:7687")
NEO4J_USER = config("NEO4J_USER", default="neo4j")
NEO4J_PASSWORD = config("NEO4J_PASSWORD", default="")

# Rate limiting
GRAPH_RAG_DEFAULT_DAILY_QUERY_LIMIT = 100
GRAPH_RAG_DEFAULT_MONTHLY_TOKEN_LIMIT = 1_000_000

# File upload
GRAPH_RAG_MAX_FILE_SIZE_MB = 50
GRAPH_RAG_ALLOWED_FILE_TYPES = ['pdf', 'docx', 'txt', 'csv', 'md']
```

---

## 8. Entity Relationship Diagram

```
┌──────────────────┐       ┌──────────────────┐
│   AgentProvider   │       │   AgentConfig     │
│   (from agents)   │       │   (from agents)   │
└────────┬─────────┘       └────────┬─────────┘
         │ 1                         │ 1
         │                           │
         │ N                         │ N
┌────────┴─────────────────────────┴──────────┐
│                 RAGInstance                    │
│  ─ name, slug, purpose                       │
│  ─ system_prompt                              │
│  ─ retrieval_config (JSON)                    │
│  ─ generation_config (JSON)                   │
│  ─ is_active, is_public                      │
└──┬────────┬────────┬────────┬───────┬───────┘
   │        │        │        │       │
   │1      │1      │1      │1     │1
   │        │        │        │       │
   │N      │N      │N      │N     │N
┌──┴──┐ ┌──┴───┐ ┌─┴──┐ ┌──┴───┐ ┌┴────────┐
│RIKB │ │RISkill│ │Conv│ │Access│ │ConfigHist│
│     │ │      │ │    │ │Perm  │ │          │
└──┬──┘ └──┬───┘ └─┬──┘ └──────┘ └──────────┘
   │N      │N      │1
   │       │       │N
┌──┴──┐ ┌──┴───┐ ┌─┴──────┐
│ KB  │ │Skill │ │Message  │
└──┬──┘ └──────┘ │─sources │
   │1            │─feedback│
   │N            └─────────┘
┌──┴───────┐
│ Document  │
│ ─status   │
│ ─metadata │
└──┬───────┘
   │1
   │N
┌──┴────────┐     ┌──────────────┐
│ DocChunk   │     │KnowledgeGraph│
│ ─content   │     │ ─status      │
│ ─embedding │     │ ─stats       │
└──┬────────┘     └──┬───────────┘
   │                  │1
   │ M2M              │N
   │            ┌─────┴──────┐
┌──┴──────┐    │             │
│GraphEntity│◄──┤      ┌──────┴────┐
│ ─name    │    │      │GraphRel   │
│ ─type    │    │      │ ─type     │
│ ─desc    │    │      │ ─weight   │
└──┬──────┘    │      └───────────┘
   │ M2M        │
┌──┴──────────┐│
│GraphCommunity││
│ ─summary     ││
│ ─rank        ││
└──────────────┘│
```
