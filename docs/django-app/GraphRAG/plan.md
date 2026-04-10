# 📋 GraphRAG System — Bản Kế Hoạch Tổng Thể

---

## 1. Tổng Quan

### Mục đích
Xây dựng hệ thống **GraphRAG (Graph-based Retrieval-Augmented Generation)** thông minh, cho phép tạo và quản lý nhiều RAG instance khác nhau phục vụ các mục đích riêng biệt (hỗ trợ khách hàng, tạo content, phân tích dữ liệu, trợ lý code...). Hệ thống kết hợp **vector search** + **knowledge graph traversal** + **community summarization** để trả lời chính xác và có ngữ cảnh sâu.

### Tại sao GraphRAG chứ không phải RAG thường?

| RAG Thường | GraphRAG |
|---|---|
| Chỉ vector similarity search | Vector + Graph traversal + Community summaries |
| Trả lời dựa trên chunks gần nhất | Hiểu mối quan hệ giữa các thực thể |
| Yếu với câu hỏi tổng hợp/so sánh | Mạnh với câu hỏi multi-hop reasoning |
| Không hiểu cấu trúc dữ liệu | Xây dựng knowledge graph tự động |
| Context rời rạc | Context có liên kết, có cấu trúc |

### Người dùng hệ thống

| Role | Quyền hạn |
|---|---|
| **Admin** (is_superuser) | Tạo, cấu hình, tinh chỉnh RAG instances. Quản lý Knowledge Base, Skills. Cấp quyền sử dụng. Xem analytics. |
| **Manager** (is_staff) | Sử dụng RAG instances được cấp quyền. Xem analytics của team. Upload documents vào KB được phép. |
| **User** (regular) | Sử dụng RAG instances được cấp quyền. Chat, nhận câu trả lời. |

### Nền tảng
- **Backend**: Django REST Framework (tích hợp vào project hiện tại)
- **AI Provider**: Sử dụng app `agents` để quản lý API keys (OpenAI, Anthropic, Google, etc.)
- **Frontend**: Next.js (admin panel + chat interface)

---

## 2. Danh Sách Tính Năng

### Nhóm A — RAG Instance Management
- ✅ Tạo nhiều RAG instance cho các mục đích khác nhau
- ✅ Mỗi instance có system prompt, model config, retrieval config riêng
- ✅ Clone RAG instance từ template có sẵn
- ✅ Bật/tắt RAG instance
- ✅ Soft delete RAG instance
- ✅ Mỗi instance chọn AI provider & model qua app `agents`
- 🔜 RAG instance templates marketplace (chia sẻ giữa các project)
- 🔜 A/B testing giữa 2 config cho cùng 1 RAG instance

### Nhóm B — Knowledge Base & Documents
- ✅ Tạo nhiều Knowledge Base (bộ tài liệu)
- ✅ Upload documents: PDF, DOCX, TXT, CSV, Markdown
- ✅ Upload images: JPG, PNG, WEBP, GIF (lưu trong KB, gán metadata/tags)
- ✅ Image captioning tự động — LLM mô tả nội dung ảnh khi upload
- ✅ Image embedding — embed caption + metadata để vector search
- ✅ Import từ URL (crawl web page)
- ✅ Import từ plain text
- ✅ Chunking tự động với chiến lược cấu hình được (fixed, semantic, recursive)
- ✅ Cấu hình chunk_size, chunk_overlap per Knowledge Base
- ✅ Xem trạng thái processing documents (pending → processing → completed/failed)
- ✅ Gán nhiều Knowledge Base cho 1 RAG instance (priority-based)
- ✅ Preview chunks sau khi processing
- 🔜 Import từ Google Drive, Notion, Confluence
- 🔜 Auto-sync documents từ URL (scheduled re-crawl)
- 🔜 Document versioning

### Nhóm C — Knowledge Graph (Graph Enhancement)
- ✅ Tự động extract entities từ documents (person, org, concept, location, event...)
- ✅ Tự động extract relationships giữa entities
- ✅ Community detection — nhóm entities liên quan thành communities
- ✅ Community summarization — LLM tạo summary cho mỗi community
- ✅ Xem và quản lý Knowledge Graph (entities, relationships)
- ✅ Graph visualization dashboard
- ✅ Rebuild graph khi documents thay đổi
- 🔜 Manual entity/relationship editing
- 🔜 Entity resolution (gộp entities trùng lặp)
- 🔜 Cross-KB graph linking

### Nhóm D — Retrieval & Search Pipeline
- ✅ Vector similarity search (embedding-based)
- ✅ Graph-based search (entity + relationship traversal)
- ✅ Hybrid search (vector + graph + keyword)
- ✅ Adaptive search — tự chọn strategy phù hợp với query
- ✅ Query decomposition — chia câu hỏi phức tạp thành sub-queries
- ✅ Reranking — cross-encoder rerank kết quả
- ✅ Self-verification — LLM kiểm tra lại câu trả lời
- ✅ Source attribution — trích dẫn nguồn rõ ràng
- ✅ Cấu hình top_k, similarity_threshold, graph_depth per instance
- ✅ Image-aware retrieval — nhận diện query cần hình ảnh, tìm ảnh liên quan trong KB
- 🔜 Query caching (similar queries → cached response)
- 🔜 Feedback loop — learn từ thumbs up/down

### Nhóm D+ — Image Intelligence
- ✅ Query image detection — tự nhận diện khi câu hỏi cần hình ảnh minh họa
- ✅ Admin toggle `images_enabled` per RAG instance — bật/tắt khả năng cung cấp ảnh
- ✅ Image retrieval — tìm ảnh trong Knowledge Base liên quan đến câu trả lời
- ✅ Image caption matching — so sánh query embedding với caption embedding của ảnh
- ✅ Image in response — trả ảnh kèm URL + caption trong response
- ✅ Multimodal input — user gửi ảnh kèm câu hỏi, LLM phân tích (nếu model hỗ trợ)
- 🔜 Image generation — tạo ảnh mới bằng DALL-E/Stable Diffusion khi KB không có ảnh phù hợp

### Nhóm E — Skills System (Tool Use)
- ✅ Pluggable skills/tools cho RAG instances
- ✅ Built-in skills: Web Search, Calculator, Summarizer, Translator
- ✅ Custom skills — admin định nghĩa skill mới qua API endpoint
- ✅ Mỗi RAG instance bật/tắt skills riêng
- ✅ Skill config override per instance
- ✅ Skills registry với input/output schema
- 🔜 Code Execution skill (sandboxed Python)
- 🔜 Database Query skill (read-only SQL)
- 🔜 Image Analysis skill (multimodal)
- 🔜 Content Generation templates (blog, report, email)

### Nhóm F — Chat & Conversation
- ✅ Chat interface với RAG instance
- ✅ Conversation history (per user per instance)
- ✅ Streaming responses (SSE)
- ✅ Source display — hiện documents/chunks/entities đã dùng
- ✅ Message feedback (thumbs up/down)
- ✅ Conversation context memory (trong phiên chat)
- ✅ Export conversation
- 🔜 Long-term memory (cross-conversation)
- 🔜 Multi-turn planning (agent-like behavior)
- 🔜 File upload in chat (analyze on the fly)

### Nhóm G — Configuration & Tuning (API-driven)
- ✅ Tất cả thông số RAG cấu hình qua API
- ✅ Default config khi tạo mới (sane defaults)
- ✅ Retrieval config: chunk_size, top_k, similarity_threshold, search_strategy, graph_depth...
- ✅ Generation config: temperature, max_tokens, top_p, tone, language...
- ✅ Config history — log mỗi lần thay đổi config
- ✅ Compare performance giữa 2 config
- 🔜 Auto-tuning — suggest optimal config dựa trên usage data
- 🔜 Config presets (fast, balanced, accurate)

### Nhóm H — Access Control & Permissions
- ✅ Admin tạo, cấu hình, tinh chỉnh RAG
- ✅ Admin cấp quyền sử dụng cho Manager/User
- ✅ Manager sử dụng RAG, upload docs vào KB được phép
- ✅ User chỉ sử dụng RAG được cấp
- ✅ Rate limiting per user per instance
- ✅ Token quota per user (daily/monthly)
- 🔜 Team-based access (assign to group)
- 🔜 API key cho external apps sử dụng RAG

### Nhóm I — Analytics & Monitoring
- ✅ Usage stats per RAG instance (queries, tokens, latency)
- ✅ Usage stats per user
- ✅ Feedback analytics (satisfaction rate)
- ✅ Popular queries
- ✅ Failed queries log
- 🔜 Cost tracking per provider
- 🔜 Performance dashboard (response time, accuracy)
- 🔜 Alerting (high error rate, quota exceeded)

---

## 3. Technology Stack

### Core Dependencies (thêm vào requirements)

```
# Vector Store
pgvector==0.3.6                    # PostgreSQL vector extension
django-pgvector==0.1.5             # Django integration

# Document Processing
langchain==0.3.x                   # RAG pipeline orchestration
langchain-community==0.3.x         # Community integrations
langchain-openai==0.2.x            # OpenAI embeddings & LLM
langchain-anthropic==0.2.x         # Anthropic LLM
unstructured[pdf,docx]==0.16.x     # Document parsing (PDF, DOCX)
tiktoken==0.8.x                    # Token counting

# Knowledge Graph
neo4j==5.26.x                      # Neo4j Python driver
networkx==3.4.x                    # Graph computation (community detection)
cdlib==0.4.x                       # Community detection algorithms

# Embeddings & Reranking
sentence-transformers==3.3.x       # Local embeddings & reranking (optional)

# Streaming
sse-starlette==2.x                 # Server-Sent Events (hoặc dùng Django Channels)
channels==4.x                      # WebSocket support (optional)
```

### Infrastructure (thêm vào docker-compose)

```yaml
# Neo4j for Knowledge Graph
neo4j:
  image: neo4j:5.26-community
  ports:
    - "7474:7474"   # Browser
    - "7687:7687"   # Bolt
  environment:
    NEO4J_AUTH: neo4j/your-password
  volumes:
    - neo4j_data:/data

# pgvector extension — thêm vào PostgreSQL image
# Dùng image: pgvector/pgvector:pg16 thay vì postgres:16
```

### Tại sao chọn stack này?

| Component | Lựa chọn | Lý do |
|---|---|---|
| Vector Store | **pgvector** | Cùng PostgreSQL, không cần thêm service. Đủ mạnh cho 100K+ vectors |
| Graph Store | **Neo4j** | Industry standard, Cypher query language, visualization built-in |
| RAG Pipeline | **LangChain** | Ecosystem lớn nhất, nhiều integrations, active development |
| Doc Parsing | **Unstructured** | Hỗ trợ nhiều format, extraction chất lượng cao |
| Embeddings | **OpenAI/Local** | text-embedding-3-small (rẻ, tốt) hoặc local model |

---

## 4. Implementation Phases

### Phase 1 — Core RAG (MVP) ⏱ ~2-3 tuần
> Mục tiêu: RAG đơn giản hoạt động end-to-end

- RAG Instance CRUD (admin only)
- Knowledge Base CRUD + Document upload (PDF, TXT, DOCX)
- Document processing pipeline (chunk → embed → store in pgvector)
- Basic vector search retrieval
- Chat API với RAG (non-streaming)
- Access permissions (admin create, user use)
- Tích hợp app `agents` cho API keys & model config

### Phase 2 — Graph Enhancement ⏱ ~2 tuần
> Mục tiêu: Nâng cấp từ RAG thường thành GraphRAG

- Entity extraction từ documents (LLM-based)
- Relationship extraction
- Knowledge Graph storage (Neo4j)
- Community detection + summarization
- Hybrid search (vector + graph)
- Graph visualization API

### Phase 3 — Intelligence Layer ⏱ ~2 tuần
> Mục tiêu: RAG trả lời thông minh hơn

- Query decomposition
- Adaptive search strategy
- Cross-encoder reranking
- Self-verification
- Source attribution chi tiết
- Streaming responses (SSE)
- Conversation memory

### Phase 4 — Skills System ⏱ ~1-2 tuần
> Mục tiêu: RAG biết dùng tools

- Skills registry & management
- Built-in skills (Web Search, Calculator, Summarizer, Translator)
- Custom skill definition qua API
- Tool-use integration trong generation pipeline
- Per-instance skill configuration

### Phase 5 — Analytics & Optimization ⏱ ~1 tuần
> Mục tiêu: Theo dõi và tối ưu

- Usage logging & analytics
- Feedback collection & analysis
- Config history & comparison
- Rate limiting & quota management
- Performance monitoring

### Phase 6 — Advanced Features 🔜
> Mục tiêu: Nâng cấp nâng cao

- Long-term conversation memory
- Config auto-tuning
- URL crawling & auto-sync
- Team-based access
- External API keys cho third-party apps
- Content generation templates

---

## 5. Kiến Trúc Tổng Quan

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                       │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐     │
│  │ Admin Panel  │  │ Chat UI      │  │ Analytics Dashboard│     │
│  │ - RAG CRUD   │  │ - Chat với   │  │ - Usage stats      │     │
│  │ - KB manage  │  │   RAG        │  │ - Feedback         │     │
│  │ - Skills     │  │ - Streaming  │  │ - Performance      │     │
│  │ - Graph view │  │ - Sources    │  │                    │     │
│  └──────┬──────┘  └──────┬───────┘  └────────┬──────────┘     │
└─────────┼────────────────┼────────────────────┼─────────────────┘
          │                │                    │
          ▼                ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Django REST API Layer                         │
│  /api/v1/graph-rag/                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐     │
│  │ RAG Instance │  │ Knowledge    │  │ Skills            │     │
│  │ Service      │  │ Base Service │  │ Service           │     │
│  └──────┬──────┘  └──────┬───────┘  └────────┬──────────┘     │
│         │                │                    │                 │
│  ┌──────┴────────────────┴────────────────────┴──────────┐     │
│  │              RAG Pipeline Service                      │     │
│  │  ┌──────────┐ ┌──────────┐ ┌────────┐ ┌───────────┐  │     │
│  │  │ Query    │ │ Retrieval│ │ Context│ │ Generation│  │     │
│  │  │ Analyzer │→│ Engine   │→│ Builder│→│ Engine    │  │     │
│  │  └──────────┘ └──────────┘ └────────┘ └───────────┘  │     │
│  │        │           │                        │         │     │
│  │        ▼           ▼                        ▼         │     │
│  │  Decompose    ┌────┴────┐            Self-Verify      │     │
│  │  Sub-queries  │ Vector  │            + Source Cite     │     │
│  │               │ Search  │                             │     │
│  │               ├─────────┤                             │     │
│  │               │ Graph   │                             │     │
│  │               │ Search  │                             │     │
│  │               ├─────────┤                             │     │
│  │               │ Keyword │                             │     │
│  │               │ Search  │                             │     │
│  │               ├─────────┤                             │     │
│  │               │ Rerank  │                             │     │
│  │               └─────────┘                             │     │
│  └───────────────────────────────────────────────────────┘     │
│                                                                 │
│  ┌──────────────────┐  ┌─────────────┐  ┌────────────────┐    │
│  │ App: agents       │  │ Celery      │  │ App: users     │    │
│  │ (API keys, model  │  │ (Async doc  │  │ (Auth, perms)  │    │
│  │  configs)         │  │  processing)│  │                │    │
│  └──────────────────┘  └─────────────┘  └────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│  Data Layer                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐    │
│  │ PostgreSQL   │  │ Neo4j        │  │ Redis             │    │
│  │ + pgvector   │  │ Knowledge    │  │ Cache + Celery    │    │
│  │ (Documents,  │  │ Graph        │  │ Broker            │    │
│  │  Vectors,    │  │ (Entities,   │  │                   │    │
│  │  RAG config) │  │  Relations)  │  │                   │    │
│  └──────────────┘  └──────────────┘  └───────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Default Configuration Values

Khi tạo mới RAG instance, các giá trị mặc định (có thể tinh chỉnh sau):

### Retrieval Defaults
```json
{
  "search_strategy": "hybrid",
  "top_k_vector": 10,
  "top_k_graph": 5,
  "top_k_final": 5,
  "similarity_threshold": 0.7,
  "graph_depth": 2,
  "community_level": 1,
  "reranking_enabled": true,
  "query_decomposition": true,
  "max_sub_queries": 3,
  "self_verification": false,
  "embedding_model": "text-embedding-3-small",
  "images_enabled": false,
  "image_top_k": 3,
  "image_similarity_threshold": 0.6
}
```

### Generation Defaults
```json
{
  "temperature": 0.7,
  "max_tokens": 2048,
  "top_p": 1.0,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0,
  "response_format": "markdown",
  "language": "vi",
  "tone": "professional",
  "include_sources": true,
  "max_context_tokens": 4096,
  "stream": true
}
```

### Knowledge Base Defaults
```json
{
  "chunk_strategy": "recursive",
  "chunk_size": 512,
  "chunk_overlap": 50,
  "embedding_model": "text-embedding-3-small"
}
```

---

## 7. Tích Hợp Với App `agents`

GraphRAG sử dụng app `agents` hiện tại để:

1. **Lấy API Key**: `AgentKeyService.get_active_key("openai")` → plain text API key
2. **Lấy Model Config**: `AgentKeyService.get_default_config("openai")` → model name + params
3. **Chọn Provider per RAG Instance**: Mỗi instance FK → AgentProvider, dùng key của provider đó
4. **Chọn Config per RAG Instance**: Mỗi instance FK → AgentConfig, dùng model/params của config đó

```python
# Ví dụ sử dụng trong RAG Pipeline
from apps.agents.services.agent_key_service import AgentKeyService

class RAGPipelineService:
    def generate(self, rag_instance, query, context):
        # Lấy API key từ provider
        api_key = AgentKeyService.get_active_key(
            rag_instance.provider.slug
        )
        # Lấy model config
        config = AgentKeyService.get_config_by_name(
            rag_instance.provider.slug,
            rag_instance.agent_config.name
        )
        # Override với generation config của RAG instance
        merged_config = {**config, **rag_instance.generation_config}
        # Call LLM...
```

---

## 8. Điểm Khác Biệt — Tại Sao GraphRAG Này Thông Minh

### 8.1 Multi-Strategy Retrieval
Không chỉ tìm chunks giống nhất, mà cũng:
- **Graph traversal**: Tìm entities liên quan qua relationships
- **Community summaries**: Trả lời câu hỏi tổng quan mà vector search không làm được
- **Adaptive strategy**: Tự phân tích query để chọn strategy phù hợp

### 8.2 Query Intelligence
- **Query decomposition**: "So sánh A và B" → Sub-query 1: "A là gì?" + Sub-query 2: "B là gì?" → Tổng hợp
- **Intent detection**: Phân biệt factual query vs analytical vs creative
- **Entity linking**: Map entities trong query với entities trong knowledge graph

### 8.3 Answer Quality
- **Self-verification**: LLM kiểm tra lại answer có consistent với context không
- **Source attribution**: Mỗi câu trả lời đính kèm nguồn cụ thể (document, chunk, entity)
- **Confidence scoring**: Đánh giá độ tin cậy của câu trả lời

### 8.4 Skills/Tools
- RAG không chỉ trả lời từ documents, mà còn biết:
  - Tìm kiếm web khi knowledge base không đủ
  - Tính toán khi cần
  - Gọi API external khi cần data thời gian thực
  - Tạo content theo template

### 8.5 Continuous Learning
- Feedback loop: thumbs up/down → improve retrieval quality
- Config tuning: dễ dàng thay đổi params và so sánh performance
- Usage analytics: hiểu patterns và optimize

---

## Xem thêm

- [architecture.md](./architecture.md) — Chi tiết models, services, folder structure
- [api-spec.md](./api-spec.md) — Đặc tả API endpoints
- [frontend-plan.md](./frontend-plan.md) — Thiết kế UX/UI frontend
