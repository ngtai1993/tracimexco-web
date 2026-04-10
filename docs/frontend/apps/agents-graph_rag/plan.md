# 📋 Agents & GraphRAG — Frontend Management Plan

## 1. Tổng Quan

### Mục đích

Xây dựng giao diện quản trị (**Admin Panel**) và giao diện người dùng (**Chat Interface**) cho hai hệ thống backend:

| App | Vai trò | Người dùng |
|-----|---------|------------|
| **Agents** | Quản lý AI providers, API keys (mã hóa), model configs | Admin |
| **GraphRAG** | Hệ thống RAG thông minh: quản lý instances, knowledge bases, chat, analytics | Admin + User |

### Mối quan hệ giữa 2 app

```
┌─────────────────────────────────────────────────────────────┐
│                      AGENTS APP                              │
│  AgentProvider ──┬── AgentAPIKey (encrypted)                │
│                  └── AgentConfig (model settings)            │
└──────────────────────────┬──────────────────────────────────┘
                           │ uses (provider + config)
┌──────────────────────────▼──────────────────────────────────┐
│                     GRAPH_RAG APP                            │
│  RAGInstance ──┬── KnowledgeBase ──┬── Document/Chunk       │
│                │                    └── KnowledgeGraph       │
│                ├── RAGSkill                                  │
│                ├── RAGConversation ── RAGMessage             │
│                ├── RAGAccessPermission                       │
│                └── RAGUsageLog / RAGConfigHistory            │
└─────────────────────────────────────────────────────────────┘
```

> **GraphRAG phụ thuộc vào Agents**: Mỗi RAG Instance phải chọn 1 `AgentProvider` và tùy chọn 1 `AgentConfig`. Do đó phải cấu hình Agents trước.

---

## 2. Danh Sách Tính Năng

### Nhóm A: Agents Management (Admin Only)

| # | Tính năng | Trạng thái |
|---|-----------|-----------|
| A1 | ✅ CRUD AI Providers (OpenAI, Anthropic, Gemini...) | MVP |
| A2 | ✅ Quản lý API Keys (thêm, sửa metadata, toggle active, xóa) | MVP |
| A3 | ✅ Key preview (hiện 8 ký tự đầu + ****) — KHÔNG BAO GIỜ hiện full key | MVP |
| A4 | ✅ Quản lý Model Configs (model name, temperature, max_tokens...) | MVP |
| A5 | ✅ Đặt default config cho provider | MVP |
| A6 | ✅ Toggle active/inactive cho providers, keys, configs | MVP |
| A7 | 🔜 Dashboard tổng quan providers (bao nhiêu key, bao nhiêu active) | Phase 2 |

### Nhóm B: RAG Instance Management (Admin Only)

| # | Tính năng | Trạng thái |
|---|-----------|-----------|
| B1 | ✅ CRUD RAG Instances (name, slug, purpose, system prompt, provider) | MVP |
| B2 | ✅ Tuning retrieval config (top_k, similarity_threshold, strategy...) | MVP |
| B3 | ✅ Tuning generation config (temperature, max_tokens, language...) | MVP |
| B4 | ✅ Clone instance | MVP |
| B5 | ✅ Gán Knowledge Bases cho instance (với priority) | MVP |
| B6 | ✅ Gán Skills cho instance | MVP |
| B7 | 🔜 Config history (xem lịch sử thay đổi config) | Phase 2 |

### Nhóm C: Knowledge Base Management (Admin Only)

| # | Tính năng | Trạng thái |
|---|-----------|-----------|
| C1 | ✅ CRUD Knowledge Bases (name, chunking strategy, embedding model) | MVP |
| C2 | ✅ Upload documents (file PDF, DOCX, TXT, CSV, MD) | MVP |
| C3 | ✅ Upload images (JPG, PNG, WEBP, GIF) | MVP |
| C4 | ✅ Thêm text document (paste nội dung) | MVP |
| C5 | ✅ Thêm URL document | MVP |
| C6 | ✅ Xem danh sách documents với processing status | MVP |
| C7 | ✅ Xem chunks của document | MVP |
| C8 | ✅ Trigger build Knowledge Graph | MVP |
| C9 | 🔜 Graph visualization (entities, relationships) | Phase 2 |

### Nhóm D: Skills Management (Admin Only)

| # | Tính năng | Trạng thái |
|---|-----------|-----------|
| D1 | ✅ Xem danh sách skills available | MVP |
| D2 | ✅ Gán/bỏ skill cho instance | MVP |
| D3 | 🔜 CRUD custom skills | Phase 2 |

### Nhóm E: Access Control (Admin Only)

| # | Tính năng | Trạng thái |
|---|-----------|-----------|
| E1 | ✅ Grant quyền truy cập instance cho user | MVP |
| E2 | ✅ Set quota (daily queries, monthly tokens) | MVP |
| E3 | ✅ Revoke access | MVP |
| E4 | ✅ Xem danh sách permissions | MVP |

### Nhóm F: Chat Interface (User)

| # | Tính năng | Trạng thái |
|---|-----------|-----------|
| F1 | ✅ Chat với RAG instance | MVP |
| F2 | ✅ Hiện sources (tài liệu tham khảo) | MVP |
| F3 | ✅ Hiện images trong response | MVP |
| F4 | ✅ Quản lý conversations (list, xem, xóa) | MVP |
| F5 | ✅ Feedback (thumbs up/down + comment) | MVP |
| F6 | ✅ Xem quota còn lại | MVP |
| F7 | 🔜 Streaming response (SSE) | Phase 2 |

### Nhóm G: Analytics (Admin Only)

| # | Tính năng | Trạng thái |
|---|-----------|-----------|
| G1 | ✅ Dashboard analytics per instance | MVP |
| G2 | ✅ Xem usage logs | MVP |
| G3 | 🔜 Charts (queries over time, token usage) | Phase 2 |

---

## 3. API Endpoints Reference

### 3.1 Agents API (`/api/v1/agents/`)

| Method | Endpoint | Mô tả | Permission |
|--------|----------|--------|-----------|
| GET | `/providers/` | List providers | Admin |
| POST | `/providers/` | Create provider | Admin |
| GET | `/providers/{slug}/` | Get provider detail | Admin |
| PATCH | `/providers/{slug}/` | Update provider | Admin |
| DELETE | `/providers/{slug}/` | Soft delete provider | Admin |
| GET | `/providers/{slug}/keys/` | List keys of provider | Admin |
| POST | `/providers/{slug}/keys/` | Add API key | Admin |
| PATCH | `/providers/{slug}/keys/{id}/` | Update key metadata | Admin |
| DELETE | `/providers/{slug}/keys/{id}/` | Soft delete key | Admin |
| GET | `/providers/{slug}/configs/` | List configs of provider | Admin |
| POST | `/providers/{slug}/configs/` | Create config | Admin |
| PATCH | `/providers/{slug}/configs/{id}/` | Update config | Admin |
| DELETE | `/providers/{slug}/configs/{id}/` | Soft delete config | Admin |

### 3.2 GraphRAG API (`/api/v1/graph-rag/`)

| Method | Endpoint | Mô tả | Permission |
|--------|----------|--------|-----------|
| **Instances** | | | |
| GET | `/instances/` | List instances | Auth |
| POST | `/instances/` | Create instance | Admin |
| GET | `/instances/{slug}/` | Instance detail | Auth |
| PATCH | `/instances/{slug}/` | Update instance | Admin |
| DELETE | `/instances/{slug}/` | Soft delete | Admin |
| PATCH | `/instances/{slug}/config/` | Update retrieval/generation config | Admin |
| POST | `/instances/{slug}/clone/` | Clone instance | Admin |
| GET | `/instances/{slug}/knowledge-bases/` | List assigned KBs | Admin |
| POST | `/instances/{slug}/knowledge-bases/` | Assign KB | Admin |
| GET | `/instances/{slug}/skills/` | List assigned skills | Admin |
| POST | `/instances/{slug}/skills/` | Assign skill | Admin |
| **Knowledge Bases** | | | |
| GET | `/knowledge-bases/` | List KBs | Admin |
| POST | `/knowledge-bases/` | Create KB | Admin |
| GET | `/knowledge-bases/{slug}/` | KB detail | Admin |
| DELETE | `/knowledge-bases/{slug}/` | Soft delete KB | Admin |
| GET | `/knowledge-bases/{slug}/documents/` | List documents | Admin |
| POST | `/knowledge-bases/{slug}/documents/upload/` | Upload file | Admin |
| POST | `/knowledge-bases/{slug}/documents/text/` | Add text doc | Admin |
| POST | `/knowledge-bases/{slug}/documents/url/` | Add URL doc | Admin |
| POST | `/knowledge-bases/{slug}/graph/build/` | Trigger graph build | Admin |
| GET | `/documents/{id}/` | Document detail | Admin |
| DELETE | `/documents/{id}/` | Soft delete doc | Admin |
| GET | `/documents/{id}/chunks/` | List chunks | Admin |
| **Chat** | | | |
| POST | `/instances/{slug}/chat/` | Send query | Auth |
| GET | `/instances/{slug}/conversations/` | List conversations | Auth |
| GET | `/instances/{slug}/conversations/{id}/` | Get messages | Auth |
| DELETE | `/instances/{slug}/conversations/{id}/` | Delete conversation | Auth |
| POST | `/messages/{id}/feedback/` | Submit feedback | Auth |
| **Access** | | | |
| GET | `/instances/{slug}/access/` | List permissions | Admin |
| POST | `/instances/{slug}/access/` | Grant access | Admin |
| DELETE | `/instances/{slug}/access/{id}/` | Revoke access | Admin |
| GET | `/instances/{slug}/my-access/` | My quota info | Auth |
| **Analytics** | | | |
| GET | `/instances/{slug}/analytics/` | Instance analytics | Admin |
| GET | `/instances/{slug}/usage-logs/` | Usage logs | Admin |
| GET | `/instances/{slug}/config-history/` | Config history | Admin |

---

## 4. Thiết Kế Routes/Pages

### 4.1 Route Map

```
/dashboard/
├── agents/                              ← Agents overview (list providers)
│   └── [slug]/                          ← Provider detail (keys + configs)
│
├── rag/                                 ← RAG instances overview
│   ├── instances/
│   │   └── [slug]/                      ← Instance detail
│   │       ├── config/                  ← Tuning retrieval & generation
│   │       ├── knowledge-bases/         ← Assigned KBs
│   │       ├── skills/                  ← Assigned skills
│   │       ├── access/                  ← Access permissions
│   │       └── analytics/               ← Usage analytics
│   │
│   └── knowledge-bases/
│       └── [slug]/                      ← KB detail
│           ├── documents/               ← Document management
│           └── graph/                   ← Knowledge graph status
│
└── chat/                                ← Chat interface (user)
    └── [slug]/                          ← Chat with specific instance
        └── [conversationId]/            ← Specific conversation
```

### 4.2 Chi Tiết Từng Route

| Route | Page | Mô tả | Quyền |
|-------|------|--------|-------|
| `/dashboard/agents` | AgentsOverview | Danh sách providers dạng card grid | Admin |
| `/dashboard/agents/[slug]` | ProviderDetail | Keys table + Configs table + tabs | Admin |
| `/dashboard/rag` | RAGOverview | Dashboard RAG instances | Admin |
| `/dashboard/rag/instances/[slug]` | InstanceDetail | Chi tiết instance, tabs config/KB/skills | Admin |
| `/dashboard/rag/instances/[slug]/config` | InstanceConfig | Form tuning retrieval + generation config | Admin |
| `/dashboard/rag/instances/[slug]/knowledge-bases` | InstanceKBs | Assigned KBs, drag-rank priority | Admin |
| `/dashboard/rag/instances/[slug]/skills` | InstanceSkills | Toggle skills on/off | Admin |
| `/dashboard/rag/instances/[slug]/access` | InstanceAccess | User permissions table | Admin |
| `/dashboard/rag/instances/[slug]/analytics` | InstanceAnalytics | Stats, logs, charts | Admin |
| `/dashboard/rag/knowledge-bases/[slug]` | KBDetail | KB info + document list | Admin |
| `/dashboard/rag/knowledge-bases/[slug]/documents` | KBDocuments | Upload/manage documents | Admin |
| `/dashboard/rag/knowledge-bases/[slug]/graph` | KBGraph | Graph build status/trigger | Admin |
| `/dashboard/chat` | ChatHome | Chọn RAG instance để chat | User |
| `/dashboard/chat/[slug]` | ChatInterface | Chat UI với instance | User |
| `/dashboard/chat/[slug]/[conversationId]` | ChatConversation | Load conversation cũ | User |

---

## 5. User Flows

### 5.1 Flow: Thiết lập hệ thống lần đầu (Admin)

```
1. Vào /dashboard/agents
2. Nhấn "Thêm Provider" → Form (name, slug, description, website)
3. Sau khi tạo → Redirect /dashboard/agents/openai
4. Nhấn "Thêm API Key" → Form (name, raw_key, priority)
   → Key được mã hóa, chỉ hiện preview "sk-proj-A..."
5. Nhấn "Thêm Config" → Form (name, model_name, config JSON, is_default)
   → Ví dụ: name="GPT-4o", model_name="gpt-4o", temperature=0.7
6. Provider sẵn sàng ✓

7. Vào /dashboard/rag → Nhấn "Tạo Knowledge Base"
8. Form (name, slug, chunk_strategy, chunk_size, embedding_model)
9. Sau khi tạo → Redirect /dashboard/rag/knowledge-bases/[slug]
10. Upload documents (file/text/URL)
    → Hiện processing status real-time (pending → processing → completed)
11. Nhấn "Build Graph" → Status changes: not_built → building → ready

12. Vào /dashboard/rag → Nhấn "Tạo RAG Instance"
13. Form wizard:
    - Step 1: Basic info (name, slug, purpose, system_prompt)
    - Step 2: Chọn Provider + Config (dropdown từ Agents app)
    - Step 3: Gán Knowledge Bases (checkbox + priority)
    - Step 4: Tuning config (với defaults hiện sẵn)
    - Step 5: Review & Create
14. Sau khi tạo → Sẵn sàng chat ✓
```

### 5.2 Flow: Chat với RAG (User)

```
1. Vào /dashboard/chat → Thấy danh sách instances mình có quyền
2. Chọn instance → /dashboard/chat/[slug]
3. Gõ câu hỏi vào chat input → Submit
4. Hiện loading skeleton cho response
5. Response hiện:
   - Nội dung trả lời (Markdown rendered)
   - Sources panel (collapsible): liệt kê tài liệu tham khảo
   - Images (nếu có): gallery dạng grid
6. Nhấn 👍/👎 để feedback → Mở box comment (optional)
7. Tiếp tục chat trong conversation
8. Sidebar trái: danh sách conversations cũ → Click để load lại
9. Nhấn "New Chat" để bắt đầu conversation mới
```

### 5.3 Flow: Quản lý API Keys (Admin)

```
1. Vào /dashboard/agents/openai
2. Tab "API Keys" hiện table:
   | Name     | Preview       | Priority | Active | Last Used  | Expires |
   | Main Key | sk-proj-A... | 1        | ✅     | 2 giờ trước | —       |
   | Backup   | sk-proj-B... | 2        | ✅     | Chưa dùng  | 30/06   |
3. Nhấn "Thêm Key" → Modal form
4. Nhấn toggle → Bật/tắt key
5. Nhấn Edit → Sửa name, priority
6. Nhấn Delete → Confirm dialog → Soft delete
```

### 5.4 Flow: Tuning Config RAG Instance (Admin)

```
1. Vào /dashboard/rag/instances/[slug]/config
2. Thấy 2 panel:
   Panel trái: Retrieval Config
   - search_strategy: dropdown (hybrid/vector/keyword)
   - top_k_vector: slider 1-50 (default 10)
   - top_k_graph: slider 1-20 (default 5)
   - similarity_threshold: slider 0-1 (default 0.7)
   - graph_depth: slider 1-5 (default 2)
   - images_enabled: toggle
   - reranking_enabled: toggle
   
   Panel phải: Generation Config
   - temperature: slider 0-2 (default 0.7)
   - max_tokens: input number (default 2048)
   - response_format: dropdown (markdown/text)
   - language: dropdown (vi/en)
   - tone: dropdown (professional/casual/technical)
   - include_sources: toggle
   - stream: toggle

3. Mỗi thay đổi → hiện nút "Save Changes" + input reason
4. Save → Config history được tự động log
```

### 5.5 Flow: Upload Documents (Admin)

```
1. Vào /dashboard/rag/knowledge-bases/[slug]/documents
2. Thấy 3 tabs upload:
   - Tab "File": Drag & drop zone (PDF, DOCX, TXT, CSV, MD, images)
   - Tab "Text": Textarea + title input
   - Tab "URL": URL input + title input
3. Upload file → Hiện progress
4. File xuất hiện trong table với status "pending" → "processing" → "completed"
5. Nếu lỗi → status "failed" + hiện error message
6. Click document → Xem chunks
```

---

## 6. Component Architecture

### 6.1 Feature Folder Structure

```
frontend/src/features/
├── agents/                              ← Agents management
│   ├── types.ts                         ← TypeScript types
│   ├── api.ts                           ← API calls (axios)
│   ├── hooks.ts                         ← React hooks (CRUD)
│   ├── components/
│   │   ├── ProviderCard.tsx             ← Card hiển thị provider
│   │   ├── ProviderForm.tsx             ← Create/Edit provider form
│   │   ├── ProviderGrid.tsx             ← Grid layout providers
│   │   ├── KeyTable.tsx                 ← Table API keys
│   │   ├── KeyForm.tsx                  ← Add/edit key form (modal)
│   │   ├── ConfigTable.tsx              ← Table configs
│   │   ├── ConfigForm.tsx               ← Add/edit config form (modal)
│   │   └── ProviderTabs.tsx             ← Tabs: Keys | Configs
│   └── index.ts
│
├── rag/                                 ← RAG management (admin)
│   ├── types.ts
│   ├── api.ts
│   ├── hooks.ts
│   ├── instances/
│   │   ├── components/
│   │   │   ├── InstanceCard.tsx         ← Card hiển thị instance
│   │   │   ├── InstanceGrid.tsx         ← Grid layout instances
│   │   │   ├── InstanceForm.tsx         ← Create instance wizard
│   │   │   ├── InstanceTabs.tsx         ← Tabs navigation
│   │   │   ├── ConfigPanel.tsx          ← Retrieval + Generation config tuning
│   │   │   ├── ConfigSlider.tsx         ← Slider control cho config values
│   │   │   ├── KBAssignList.tsx         ← Danh sách assigned KBs
│   │   │   ├── SkillToggleList.tsx      ← Toggle skills on/off
│   │   │   ├── AccessTable.tsx          ← Permissions table
│   │   │   ├── AccessGrantForm.tsx      ← Grant access modal
│   │   │   ├── AnalyticsDashboard.tsx   ← Stats cards + usage chart
│   │   │   ├── UsageLogTable.tsx        ← Usage logs table
│   │   │   └── ConfigHistoryTable.tsx   ← Config history table
│   │   └── index.ts
│   │
│   ├── knowledge-bases/
│   │   ├── components/
│   │   │   ├── KBCard.tsx               ← Card hiển thị KB
│   │   │   ├── KBGrid.tsx              ← Grid layout KBs
│   │   │   ├── KBForm.tsx               ← Create KB form
│   │   │   ├── DocumentTable.tsx        ← Table documents + status
│   │   │   ├── DocumentUploadForm.tsx   ← File upload (drag & drop)
│   │   │   ├── DocumentTextForm.tsx     ← Add text document
│   │   │   ├── DocumentURLForm.tsx      ← Add URL document
│   │   │   ├── DocumentUploadTabs.tsx   ← Tabs: File | Text | URL
│   │   │   ├── ChunkViewer.tsx          ← Xem chunks của document
│   │   │   ├── GraphStatusCard.tsx      ← Graph build status
│   │   │   └── ProcessingStatusBadge.tsx ← Badge pending/processing/done/failed
│   │   └── index.ts
│   │
│   └── index.ts
│
└── chat/                                ← Chat interface (user)
    ├── types.ts
    ├── api.ts
    ├── hooks.ts
    ├── components/
    │   ├── ChatLayout.tsx               ← Sidebar conversations + main chat
    │   ├── ChatSidebar.tsx              ← Conversations list
    │   ├── ChatWindow.tsx               ← Messages area
    │   ├── ChatInput.tsx                ← Input box + send button
    │   ├── ChatMessage.tsx              ← Single message (user/assistant)
    │   ├── MessageContent.tsx           ← Markdown rendered content
    │   ├── SourcesPanel.tsx             ← Collapsible sources list
    │   ├── ImageGallery.tsx             ← Grid of returned images
    │   ├── FeedbackButtons.tsx          ← 👍👎 + comment box
    │   ├── InstanceSelector.tsx         ← Choose RAG instance to chat
    │   ├── QuotaIndicator.tsx           ← Hiện quota còn lại
    │   ├── TypingIndicator.tsx          ← Loading dots animation
    │   └── EmptyChat.tsx                ← Empty state khi chưa chat
    └── index.ts
```

### 6.2 Shared UI Components Cần Thêm

Ngoài components `ui/` đã có (Button, Input, Modal, Toast, Badge, Avatar, etc.), cần thêm:

| Component | Dùng ở đâu | Mô tả |
|-----------|-----------|-------|
| `Tabs` | ProviderTabs, InstanceTabs, DocumentUploadTabs | Tab navigation component |
| `Slider` | ConfigPanel (temperature, top_k...) | Range slider với label + value |
| `Select` | InstanceForm, ConfigPanel (strategy, language) | Dropdown select |
| `Switch` | Config toggles, key active toggle | On/off boolean toggle |
| `Table` | KeyTable, ConfigTable, DocumentTable, etc. | Reusable data table |
| `EmptyState` | Khi danh sách trống | Illustration + message + action |
| `StatusBadge` | Document processing, graph status | Color-coded status indicator |
| `JsonEditor` | AgentConfig.config_json | Simple JSON text editor |
| `DragDropZone` | Document upload | Drag & drop file upload area |
| `MarkdownRenderer` | ChatMessage content | Safe markdown rendering |
| `Skeleton` | Loading states | Placeholder skeleton loaders |
| `Breadcrumb` | All detail pages | Navigation breadcrumb |
| `StepWizard` | Create instance wizard | Multi-step form wrapper |
| `SearchInput` | List pages | Search/filter input |
| `Tooltip` | Config labels | Info tooltip on hover |

---

## 7. TypeScript Types

### 7.1 Agents Types (`features/agents/types.ts`)

```typescript
// ── Provider ──────────────────────────────
export interface AgentProvider {
  id: string;
  name: string;
  slug: string;
  description: string;
  website_url: string;
  is_active: boolean;
  keys_count: number;
  active_keys_count: number;
  created_at: string;
  updated_at: string;
}

export interface AgentProviderInput {
  name: string;
  slug: string;
  description?: string;
  website_url?: string;
  is_active?: boolean;
}

// ── API Key ───────────────────────────────
export interface AgentAPIKey {
  id: string;
  name: string;
  key_preview: string;    // "sk-proj-A...****"
  is_active: boolean;
  priority: number;
  last_used_at: string | null;
  expires_at: string | null;
  created_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface AgentAPIKeyInput {
  name: string;
  raw_key: string;        // Plain text — gửi 1 lần, không bao giờ nhận lại
  priority?: number;
  expires_at?: string | null;
}

export interface AgentAPIKeyUpdate {
  name?: string;
  priority?: number;
  is_active?: boolean;
  expires_at?: string | null;
}

// ── Config ────────────────────────────────
export interface AgentConfig {
  id: string;
  name: string;
  model_name: string;
  config_json: Record<string, unknown>;
  is_default: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AgentConfigInput {
  name: string;
  model_name: string;
  config_json?: Record<string, unknown>;
  is_default?: boolean;
  is_active?: boolean;
}
```

### 7.2 GraphRAG Types (`features/rag/types.ts`)

```typescript
// ── RAG Instance ──────────────────────────
export interface RAGInstance {
  id: string;
  name: string;
  slug: string;
  description: string;
  purpose: string;
  system_prompt: string;
  provider_name: string;
  agent_config_name: string | null;
  retrieval_config: RetrievalConfig;
  generation_config: GenerationConfig;
  is_active: boolean;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface RetrievalConfig {
  search_strategy: "hybrid" | "vector" | "keyword" | "graph";
  top_k_vector: number;
  top_k_graph: number;
  top_k_final: number;
  similarity_threshold: number;
  graph_depth: number;
  embedding_model: string;
  images_enabled: boolean;
  reranking_enabled: boolean;
  query_decomposition: boolean;
}

export interface GenerationConfig {
  temperature: number;
  max_tokens: number;
  response_format: "markdown" | "text";
  language: "vi" | "en";
  tone: "professional" | "casual" | "technical";
  include_sources: boolean;
  stream: boolean;
}

// ── Knowledge Base ────────────────────────
export interface KnowledgeBase {
  id: string;
  name: string;
  slug: string;
  description: string;
  chunk_strategy: "fixed" | "recursive" | "semantic";
  chunk_size: number;
  chunk_overlap: number;
  embedding_model: string;
  embedding_dimensions: number;
  document_count: number;
  image_count: number;
  total_chunks: number;
  is_active: boolean;
  graph_status: "not_built" | "building" | "ready" | "failed" | null;
  created_at: string;
  updated_at: string;
}

// ── Document ──────────────────────────────
export interface Document {
  id: string;
  title: string;
  description: string;
  source_type: "file" | "text" | "url";
  is_image: boolean;
  image_caption: string;
  image_tags: string[];
  processing_status: "pending" | "processing" | "completed" | "failed";
  processing_error: string;
  chunk_count: number;
  token_count: number;
  kb_name: string;
  metadata: Record<string, unknown>;
  processed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentChunk {
  id: string;
  chunk_index: number;
  content: string;
  token_count: number;
  is_image_chunk: boolean;
  metadata: Record<string, unknown>;
  created_at: string;
}

// ── Conversation ──────────────────────────
export interface RAGConversation {
  id: string;
  title: string;
  message_count: number;
  last_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface RAGMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  sources: Source[];
  images: ImageResult[];
  skills_used: string[];
  metadata: MessageMetadata;
  feedback: "positive" | "negative" | null;
  feedback_comment: string;
  created_at: string;
}

export interface Source {
  chunk_id: string;
  document_title: string;
  content: string;
  score: number;
}

export interface ImageResult {
  id: string;
  url: string;
  caption: string;
  score: number;
}

export interface MessageMetadata {
  tokens_in: number;
  tokens_out: number;
  latency_ms: number;
  retrieval_strategy: string;
  model: string;
}

// ── Access ────────────────────────────────
export interface RAGAccessPermission {
  id: string;
  user_email: string;
  access_level: "use" | "manage";
  daily_query_limit: number;
  monthly_token_limit: number;
  expires_at: string | null;
  granted_by_email: string | null;
  created_at: string;
}

// ── Analytics ─────────────────────────────
export interface RAGAnalytics {
  total_queries: number;
  unique_users: number;
  total_tokens_in: number;
  total_tokens_out: number;
  avg_latency_ms: number;
  total_images: number;
}

export interface UsageLog {
  id: string;
  query: string;
  retrieval_strategy: string;
  tokens_in: number;
  tokens_out: number;
  latency_ms: number;
  sources_count: number;
  images_returned: number;
  created_at: string;
}

export interface ConfigHistory {
  id: string;
  config_type: "retrieval" | "generation";
  old_value: Record<string, unknown>;
  new_value: Record<string, unknown>;
  reason: string;
  changed_by_email: string | null;
  created_at: string;
}
```

### 7.3 Chat Types (`features/chat/types.ts`)

```typescript
export interface ChatQueryInput {
  query: string;
  conversation_id?: string | null;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
  images: ImageResult[];
  conversation_id: string;
  message_id: string;
  metadata: MessageMetadata;
}

export interface MyAccess {
  has_access: boolean;
  access_level?: string;
  daily_queries_used?: number;
  daily_query_limit?: number;
  monthly_tokens_used?: number;
  monthly_token_limit?: number;
  note?: string;
}

export interface FeedbackInput {
  feedback: "positive" | "negative";
  comment?: string;
}
```

---

## 8. API Layer

### 8.1 Agents API (`features/agents/api.ts`)

```typescript
import api from "@/lib/api";
import { ApiResponse } from "@/types/api";

const BASE = "/agents/providers";

export const agentApi = {
  // Providers
  listProviders: (includeInactive = false) =>
    api.get<ApiResponse<AgentProvider[]>>(BASE, {
      params: { include_inactive: includeInactive },
    }),
  getProvider: (slug: string) =>
    api.get<ApiResponse<AgentProvider>>(`${BASE}/${slug}/`),
  createProvider: (data: AgentProviderInput) =>
    api.post<ApiResponse<AgentProvider>>(BASE + "/", data),
  updateProvider: (slug: string, data: Partial<AgentProviderInput>) =>
    api.patch<ApiResponse<AgentProvider>>(`${BASE}/${slug}/`, data),
  deleteProvider: (slug: string) =>
    api.delete(`${BASE}/${slug}/`),

  // Keys
  listKeys: (slug: string) =>
    api.get<ApiResponse<AgentAPIKey[]>>(`${BASE}/${slug}/keys/`),
  createKey: (slug: string, data: AgentAPIKeyInput) =>
    api.post<ApiResponse<AgentAPIKey>>(`${BASE}/${slug}/keys/`, data),
  updateKey: (slug: string, keyId: string, data: AgentAPIKeyUpdate) =>
    api.patch<ApiResponse<AgentAPIKey>>(`${BASE}/${slug}/keys/${keyId}/`, data),
  deleteKey: (slug: string, keyId: string) =>
    api.delete(`${BASE}/${slug}/keys/${keyId}/`),

  // Configs
  listConfigs: (slug: string) =>
    api.get<ApiResponse<AgentConfig[]>>(`${BASE}/${slug}/configs/`),
  createConfig: (slug: string, data: AgentConfigInput) =>
    api.post<ApiResponse<AgentConfig>>(`${BASE}/${slug}/configs/`, data),
  updateConfig: (slug: string, configId: string, data: Partial<AgentConfigInput>) =>
    api.patch<ApiResponse<AgentConfig>>(`${BASE}/${slug}/configs/${configId}/`, data),
  deleteConfig: (slug: string, configId: string) =>
    api.delete(`${BASE}/${slug}/configs/${configId}/`),
};
```

### 8.2 RAG API (`features/rag/api.ts`)

```typescript
import api from "@/lib/api";
import { ApiResponse } from "@/types/api";

const INST = "/graph-rag/instances";
const KB = "/graph-rag/knowledge-bases";
const DOC = "/graph-rag/documents";
const MSG = "/graph-rag/messages";

export const ragApi = {
  // Instances
  listInstances: (includeInactive = false) =>
    api.get<ApiResponse<RAGInstance[]>>(INST, {
      params: { include_inactive: includeInactive },
    }),
  getInstance: (slug: string) =>
    api.get<ApiResponse<RAGInstance>>(`${INST}/${slug}/`),
  createInstance: (data: RAGInstanceInput) =>
    api.post<ApiResponse<RAGInstance>>(INST + "/", data),
  updateInstance: (slug: string, data: Partial<RAGInstanceInput>) =>
    api.patch<ApiResponse<RAGInstance>>(`${INST}/${slug}/`, data),
  deleteInstance: (slug: string) =>
    api.delete(`${INST}/${slug}/`),
  updateConfig: (slug: string, data: ConfigUpdateInput) =>
    api.patch<ApiResponse<RAGInstance>>(`${INST}/${slug}/config/`, data),
  cloneInstance: (slug: string, data: { new_name: string; new_slug: string }) =>
    api.post<ApiResponse<RAGInstance>>(`${INST}/${slug}/clone/`, data),

  // Instance KBs & Skills
  listInstanceKBs: (slug: string) =>
    api.get<ApiResponse<InstanceKBAssignment[]>>(`${INST}/${slug}/knowledge-bases/`),
  assignKB: (slug: string, data: { knowledge_base_id: string; priority: number }) =>
    api.post(`${INST}/${slug}/knowledge-bases/`, data),
  listInstanceSkills: (slug: string) =>
    api.get<ApiResponse<InstanceSkillAssignment[]>>(`${INST}/${slug}/skills/`),
  assignSkill: (slug: string, data: { skill_id: string; config_override?: object }) =>
    api.post(`${INST}/${slug}/skills/`, data),

  // Knowledge Bases
  listKBs: (includeInactive = false) =>
    api.get<ApiResponse<KnowledgeBase[]>>(KB, {
      params: { include_inactive: includeInactive },
    }),
  getKB: (slug: string) =>
    api.get<ApiResponse<KnowledgeBase>>(`${KB}/${slug}/`),
  createKB: (data: KBInput) =>
    api.post<ApiResponse<KnowledgeBase>>(KB + "/", data),
  deleteKB: (slug: string) =>
    api.delete(`${KB}/${slug}/`),

  // Documents
  listDocuments: (kbSlug: string, isImage?: boolean) =>
    api.get<ApiResponse<Document[]>>(`${KB}/${kbSlug}/documents/`, {
      params: isImage !== undefined ? { is_image: isImage } : {},
    }),
  uploadDocument: (kbSlug: string, formData: FormData) =>
    api.post<ApiResponse<Document>>(`${KB}/${kbSlug}/documents/upload/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  addTextDocument: (kbSlug: string, data: { title: string; content_text: string; description?: string }) =>
    api.post<ApiResponse<Document>>(`${KB}/${kbSlug}/documents/text/`, data),
  addURLDocument: (kbSlug: string, data: { title: string; source_url: string; description?: string }) =>
    api.post<ApiResponse<Document>>(`${KB}/${kbSlug}/documents/url/`, data),
  getDocument: (docId: string) =>
    api.get<ApiResponse<Document>>(`${DOC}/${docId}/`),
  deleteDocument: (docId: string) =>
    api.delete(`${DOC}/${docId}/`),
  listChunks: (docId: string) =>
    api.get<ApiResponse<DocumentChunk[]>>(`${DOC}/${docId}/chunks/`),
  buildGraph: (kbSlug: string) =>
    api.post(`${KB}/${kbSlug}/graph/build/`),

  // Access
  listAccess: (slug: string) =>
    api.get<ApiResponse<RAGAccessPermission[]>>(`${INST}/${slug}/access/`),
  grantAccess: (slug: string, data: GrantAccessInput) =>
    api.post<ApiResponse<RAGAccessPermission>>(`${INST}/${slug}/access/`, data),
  revokeAccess: (slug: string, permId: string) =>
    api.delete(`${INST}/${slug}/access/${permId}/`),
  getMyAccess: (slug: string) =>
    api.get<ApiResponse<MyAccess>>(`${INST}/${slug}/my-access/`),

  // Analytics
  getAnalytics: (slug: string, days = 7) =>
    api.get<ApiResponse<RAGAnalytics>>(`${INST}/${slug}/analytics/`, {
      params: { days },
    }),
  listUsageLogs: (slug: string, limit = 50) =>
    api.get<ApiResponse<UsageLog[]>>(`${INST}/${slug}/usage-logs/`, {
      params: { limit },
    }),
  listConfigHistory: (slug: string, limit = 20) =>
    api.get<ApiResponse<ConfigHistory[]>>(`${INST}/${slug}/config-history/`, {
      params: { limit },
    }),
};

export const chatApi = {
  sendQuery: (slug: string, data: ChatQueryInput) =>
    api.post<ApiResponse<ChatResponse>>(`${INST}/${slug}/chat/`, data),
  listConversations: (slug: string) =>
    api.get<ApiResponse<RAGConversation[]>>(`${INST}/${slug}/conversations/`),
  getConversation: (slug: string, conversationId: string) =>
    api.get<ApiResponse<RAGMessage[]>>(`${INST}/${slug}/conversations/${conversationId}/`),
  deleteConversation: (slug: string, conversationId: string) =>
    api.delete(`${INST}/${slug}/conversations/${conversationId}/`),
  submitFeedback: (messageId: string, data: FeedbackInput) =>
    api.post(`${MSG}/${messageId}/feedback/`, data),
};
```

---

## 9. UX Considerations

### 9.1 States cho mỗi tính năng

| Tính năng | Loading | Empty | Error | Success |
|-----------|---------|-------|-------|---------|
| **Provider List** | Skeleton cards (3 cards) | "Chưa có AI Provider nào. Thêm provider đầu tiên để bắt đầu." + CTA button | Toast error | — |
| **Key Table** | Skeleton rows (3 rows) | "Provider chưa có API key. Thêm key để sử dụng." | Toast error | Toast "Key đã được thêm" |
| **Config Table** | Skeleton rows | "Chưa có config. Thêm config mới." | Toast error | Toast "Config đã được lưu" |
| **RAG Instances** | Skeleton cards | "Chưa có RAG Instance. Tạo instance đầu tiên." + CTA | Toast error | Toast "Instance đã được tạo" |
| **Config Tuning** | Skeleton panel | — (luôn có defaults) | Toast error | Toast "Config đã được cập nhật" |
| **Knowledge Bases** | Skeleton cards | "Chưa có Knowledge Base. Tạo KB để bắt đầu." | Toast error | — |
| **Documents** | Skeleton table | "KB chưa có tài liệu. Upload hoặc thêm document." | Toast error | Toast "Document đang được xử lý" |
| **Chat** | Typing indicator (3 dots) | EmptyChat component: "Gửi câu hỏi để bắt đầu trò chuyện" | Inline error above input | — |
| **Conversations** | Skeleton sidebar | "Chưa có cuộc trò chuyện nào" | Toast error | — |

### 9.2 Form Validation (Zod Schemas)

| Form | Validation Rules |
|------|-----------------|
| Provider | name: required, slug: required + pattern, website_url: optional valid URL |
| API Key | name: required, raw_key: required min 10 chars, priority: min 1 |
| Config | name: required, model_name: required, config_json: valid JSON |
| RAG Instance | name: required, slug: required, system_prompt: required min 10 chars, provider_id: required UUID |
| Knowledge Base | name: required, slug: required, chunk_size: 100-4096, chunk_overlap: 0-500 |
| Document Upload | title: required, file: required + type validation |
| Chat Query | query: required max 4000 chars |
| Grant Access | user_id: required UUID, daily_limit: min 1, monthly_limit: min 1000 |

### 9.3 Optimistic Updates

| Action | Optimistic? | Lý do |
|--------|------------|-------|
| Toggle key active | ✅ | Toggle nhanh, revert nếu lỗi |
| Toggle skill enabled | ✅ | Tương tự |
| Delete provider/key/config | ❌ | Destructive action, chờ confirm + API |
| Create anything | ❌ | Cần ID từ server |
| Send chat query | ❌ | Cần response từ RAG pipeline |
| Submit feedback | ✅ | Update UI ngay, API gọi ngầm |

### 9.4 Security Notes

- **KHÔNG BAO GIỜ** hiện full API key ở frontend — chỉ hiện `key_preview`
- `raw_key` chỉ gửi 1 lần khi tạo key, không bao giờ nhận lại
- Tất cả admin routes phải check `user.is_staff` ở middleware
- Chat routes check access permission qua `my-access` API
- File upload validate type + size ở cả client (Zod) và server

---

## 10. Sidebar Navigation

Cần update Sidebar component để thêm menu items cho Agents và RAG:

```
📊 Dashboard          → /dashboard
🤖 AI Providers       → /dashboard/agents
📚 RAG System         → /dashboard/rag
   ├── Instances      → /dashboard/rag (tab instances)
   └── Knowledge Bases → /dashboard/rag (tab KBs)
💬 Chat               → /dashboard/chat
🎨 Appearance         → /dashboard/appearance
👤 Profile            → /profile
```

---

## 11. Phân Chia Phase Triển Khai

### Phase 1 — MVP Core (ưu tiên cao nhất)

**Sprint 1: Agents Management**
1. UI components: Tabs, Select, Switch, Table, Slider
2. `features/agents/` — types, api, hooks
3. Pages: `/dashboard/agents`, `/dashboard/agents/[slug]`
4. CRUD providers, keys, configs

**Sprint 2: Knowledge Base**
1. UI components: DragDropZone, StatusBadge, SearchInput
2. `features/rag/knowledge-bases/` — types, api, hooks
3. Pages: `/dashboard/rag/knowledge-bases/[slug]`, `/dashboard/rag/knowledge-bases/[slug]/documents`
4. CRUD KBs, upload documents, view chunks, trigger graph build

**Sprint 3: RAG Instances**
1. UI components: StepWizard, JsonEditor
2. `features/rag/instances/` — types, api, hooks
3. Pages: `/dashboard/rag`, `/dashboard/rag/instances/[slug]`
4. CRUD instances, config tuning, assign KBs/skills, access control

**Sprint 4: Chat Interface**
1. UI components: MarkdownRenderer
2. `features/chat/` — types, api, hooks
3. Pages: `/dashboard/chat`, `/dashboard/chat/[slug]`
4. Chat UI, conversations, sources, feedback

**Sprint 5: Analytics**
1. `features/rag/instances/analytics/`
2. Pages: `/dashboard/rag/instances/[slug]/analytics`
3. Stats dashboard, usage logs

### Phase 2 — Enhancement

- SSE streaming cho chat responses
- Graph visualization (react-force-graph)
- Config history diff viewer
- Charts (queries over time, token usage)
- CRUD custom skills
- Batch document upload
- Export conversations

---

## 12. Hướng Dẫn Triển Khai Cho Developer

### Bước 1: Tạo UI components cần thiết

Trước khi tạo features, hãy tạo shared UI components:
```
src/components/ui/Tabs.tsx
src/components/ui/Select.tsx
src/components/ui/Switch.tsx
src/components/ui/Table.tsx
src/components/ui/Slider.tsx
src/components/ui/StatusBadge.tsx
src/components/ui/EmptyState.tsx
src/components/ui/Breadcrumb.tsx
src/components/ui/SearchInput.tsx
src/components/ui/Skeleton.tsx
src/components/ui/Tooltip.tsx
```

### Bước 2: Tạo feature Agents

```bash
# Tạo folder structure
mkdir -p src/features/agents/components

# Tạo files theo thứ tự:
# 1. types.ts       — copy types từ section 7.1
# 2. api.ts         — copy API layer từ section 8.1
# 3. hooks.ts       — tạo hooks dùng api.ts
# 4. components/    — tạo components từ section 6.1
```

**Hooks pattern** (theo convention existing):
```typescript
// features/agents/hooks.ts
import { useState, useEffect, useCallback } from "react";
import { agentApi } from "./api";

export function useProviders() {
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  // fetch on mount, return { providers, loading, refetch }
}

export function useProviderDetail(slug: string) {
  // fetch provider + keys + configs
  // return { provider, keys, configs, loading }
}

export function useCreateProvider() {
  // return { create, loading, error }
}
// ... etc
```

### Bước 3: Tạo pages

```bash
# Agents pages
mkdir -p src/app/(main)/dashboard/agents/[slug]

# RAG pages
mkdir -p src/app/(main)/dashboard/rag/instances/[slug]/config
mkdir -p src/app/(main)/dashboard/rag/instances/[slug]/knowledge-bases
mkdir -p src/app/(main)/dashboard/rag/instances/[slug]/skills
mkdir -p src/app/(main)/dashboard/rag/instances/[slug]/access
mkdir -p src/app/(main)/dashboard/rag/instances/[slug]/analytics
mkdir -p src/app/(main)/dashboard/rag/knowledge-bases/[slug]/documents
mkdir -p src/app/(main)/dashboard/rag/knowledge-bases/[slug]/graph

# Chat pages
mkdir -p src/app/(main)/dashboard/chat/[slug]/[conversationId]
```

### Bước 4: Update Sidebar

Thêm menu items cho Agents, RAG, Chat vào `src/components/layout/Sidebar.tsx`.

### Bước 5: Update middleware

Thêm `/dashboard/agents`, `/dashboard/rag`, `/dashboard/chat` vào protected routes trong `src/proxy.ts`.

---

## 13. Conventions & Patterns (tuân theo project hiện tại)

| Convention | Pattern |
|-----------|---------|
| State management | useState + custom hooks (không dùng Redux/Zustand) |
| API calls | axios instance từ `@/lib/api` với auto-refresh token |
| Form validation | Zod schemas, validate trước khi gọi API |
| Error handling | Toast notifications cho API errors |
| Styling | Tailwind CSS với CSS variables từ appearance API |
| Components | Feature-based folder, tái sử dụng từ `components/ui/` |
| Types | Strict TypeScript, types riêng cho mỗi feature |
| Loading | Skeleton components cho initial load |
| Empty states | Dedicated EmptyState component với CTA |
| Modals | Modal component cho forms nhỏ (add key, grant access) |
| Tables | Reusable Table component với sort/filter |
| Navigation | Breadcrumb + Sidebar + Tabs cho nested views |
