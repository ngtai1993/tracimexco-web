# GraphRAG — Thiết Kế UX/UI Frontend

---

## 1. Danh Sách Routes

### Admin Routes (is_superuser)

| Route | Mô tả | Permission |
|---|---|---|
| `/admin/graph-rag` | Dashboard tổng quan GraphRAG | Admin |
| `/admin/graph-rag/instances` | Danh sách RAG instances | Admin |
| `/admin/graph-rag/instances/new` | Tạo RAG instance mới | Admin |
| `/admin/graph-rag/instances/[slug]` | Chi tiết & config RAG instance | Admin |
| `/admin/graph-rag/instances/[slug]/config` | Tuning retrieval/generation config | Admin |
| `/admin/graph-rag/instances/[slug]/knowledge-bases` | Quản lý KB assignments | Admin |
| `/admin/graph-rag/instances/[slug]/skills` | Quản lý skills assignments | Admin |
| `/admin/graph-rag/instances/[slug]/permissions` | Quản lý quyền truy cập | Admin |
| `/admin/graph-rag/instances/[slug]/analytics` | Analytics cho instance | Admin |
| `/admin/graph-rag/instances/[slug]/test` | Test query (dry run) | Admin |
| `/admin/graph-rag/knowledge-bases` | Danh sách Knowledge Bases | Admin |
| `/admin/graph-rag/knowledge-bases/new` | Tạo KB mới | Admin |
| `/admin/graph-rag/knowledge-bases/[slug]` | Chi tiết KB + documents | Admin |
| `/admin/graph-rag/knowledge-bases/[slug]/graph` | Knowledge Graph visualization | Admin |
| `/admin/graph-rag/skills` | Quản lý skills | Admin |
| `/admin/graph-rag/skills/new` | Tạo custom skill | Admin |
| `/admin/graph-rag/analytics` | Global analytics dashboard | Admin |

### User Routes (All authenticated)

| Route | Mô tả | Permission |
|---|---|---|
| `/chat` | Danh sách RAG instances có quyền dùng | All |
| `/chat/[slug]` | Chat interface với RAG instance | Có quyền |
| `/chat/[slug]/[conversation_id]` | Tiếp tục conversation cũ | Owner |
| `/chat/history` | Lịch sử conversations | All |

---

## 2. User Flows

### Flow A: Admin tạo RAG Instance mới

```
1. Admin vào /admin/graph-rag/instances
2. Nhấn "Tạo RAG Instance"
3. Form wizard 4 bước:

   Bước 1 — Thông tin cơ bản:
   ├── Name, Slug (auto-generate), Description
   ├── Purpose (dropdown: customer_support, content_creation, ...)
   └── System Prompt (textarea lớn, có template suggestions)

   Bước 2 — Chọn AI Model:
   ├── Provider (dropdown từ app agents: OpenAI, Anthropic, ...)
   ├── Model Config (dropdown: GPT-4o, GPT-4o-mini, Claude 3.5, ...)
   └── Preview: model name, cost estimate

   Bước 3 — Cấu hình RAG (optional, có defaults):
   ├── Retrieval Config (collapsible, show defaults)
   │   ├── Search Strategy: hybrid / vector / graph / adaptive
   │   ├── Top K Vector: slider (1-50, default 10)
   │   ├── Top K Graph: slider (1-20, default 5)
   │   ├── Similarity Threshold: slider (0-1, default 0.7)
   │   ├── Reranking: toggle (default on)
   │   ├── Query Decomposition: toggle (default on)
   │   └── Self Verification: toggle (default off)
   └── Generation Config (collapsible)
       ├── Temperature: slider (0-2, default 0.7)
       ├── Max Tokens: input (default 2048)
       ├── Tone: dropdown (professional, casual, formal, creative)
       ├── Language: dropdown (vi, en, auto)
       └── Include Sources: toggle (default on)

   Bước 4 — Review & Create:
   ├── Summary of all settings
   ├── Nhấn "Tạo" → redirect to instance detail
   └── Nhấn "Tạo & Thêm Knowledge Base" → redirect to KB assignment

4. Instance created → Admin tiếp tục:
   - Gán Knowledge Bases
   - Gán Skills
   - Cấp quyền cho users
   - Test query
```

### Flow B: Admin tinh chỉnh RAG Config

```
1. Admin vào /admin/graph-rag/instances/[slug]/config
2. Thấy 2 tabs: "Retrieval Config" | "Generation Config"

   Tab Retrieval:
   ├── Mỗi param có: label, current value, default value, description
   ├── Sliders cho numeric values
   ├── Toggles cho boolean values
   ├── Dropdowns cho enum values
   ├── Realtime preview: "Changes: top_k_vector 10→20, reranking: on→off"
   └── "Reason" textarea (optional, cho config history)

3. Nhấn "Lưu" → API call → Success toast
4. Bên phải: Config History panel (timeline)
   └── Click entry → xem diff cũ vs mới

5. Quick actions:
   ├── "Reset về mặc định" → confirm dialog → reset
   ├── "Clone config" → copy sang instance khác
   └── "Test với config này" → mở test panel
```

### Flow C: Admin quản lý Knowledge Base

```
1. Admin vào /admin/graph-rag/knowledge-bases/[slug]
2. Thấy tabs: "Documents" | "Knowledge Graph" | "Settings"

   Tab Documents:
   ├── Header: Stats (total docs, total chunks, processing status)
   ├── Upload area (drag & drop) → multipart upload → toast "Processing..."
   ├── "Add URL" button → modal: nhập URL → submit
   ├── "Add Text" button → modal: title + textarea → submit
   ├── Table danh sách documents:
   │   ├── Title | Source Type | Status | Chunks | Entities | Actions
   │   ├── Status badges: 🟡 Pending, 🔵 Processing, 🟢 Completed, 🔴 Failed
   │   ├── Expand row → preview first 3 chunks
   │   └── Actions: View chunks, Reprocess, Delete
   └── Auto-refresh khi có docs đang processing (polling mỗi 5s)

   Tab Knowledge Graph:
   ├── Graph Status banner: "Ready ✅ | Building 🔄 | Not Built ⚪"
   ├── Stats: entities, relationships, communities
   ├── "Build Graph" / "Rebuild" button
   ├── Graph Visualization (interactive):
   │   ├── D3.js / react-force-graph
   │   ├── Nodes = entities (color by type, size by connections)
   │   ├── Edges = relationships (thickness by weight)
   │   ├── Click node → sidebar: entity detail + relationships
   │   ├── Filter by entity type
   │   └── Zoom, pan, search node
   └── Communities list → click → show entities + summary

   Tab Settings:
   ├── Chunk Strategy, Size, Overlap
   ├── Embedding Model
   ├── Warning: "Thay đổi settings cần reprocess documents"
   └── Danger zone: Delete KB
```

### Flow D: User chat với RAG

```
1. User vào /chat → thấy grid cards các RAG instances có quyền
   ├── Mỗi card: icon, name, description, purpose badge
   ├── "Customer Support Bot" — "Hỗ trợ khách hàng"
   ├── "Content Writer" — "Tạo nội dung"
   └── Click card → /chat/[slug]

2. Chat Interface:
   ├── Sidebar trái: conversation history (filterable)
   │   ├── "New Chat" button
   │   ├── List conversations: title, last message preview, date
   │   └── Click → load conversation
   │
   ├── Main chat area:
   │   ├── Header: RAG instance name + description
   │   ├── Messages:
   │   │   ├── User message (align right)
   │   │   ├── Assistant message (align left):
   │   │   │   ├── Markdown rendered content
   │   │   │   ├── Source references (numbered [1], [2])
   │   │   │   ├── Expandable "Sources" section:
   │   │   │   │   ├── 📄 "Product Manual v3, p.15" — preview text
   │   │   │   │   ├── 🔗 "Entity: Sản phẩm X" — description
   │   │   │   │   └── 🌐 "Web Search: ..." (if skill used)
   │   │   │   ├── Feedback buttons: 👍 👎
   │   │   │   └── Metadata (collapse): tokens, latency, model
   │   │   └── Streaming: tokens appear one by one, status bar shows step
   │   │
   │   ├── Status bar (during processing):
   │   │   ├── "🔍 Đang tìm kiếm tài liệu..." (retrieving)
   │   │   ├── "🧠 Đang phân tích..." (analyzing)
   │   │   ├── "✍️ Đang tạo câu trả lời..." (generating)
   │   │   └── Disappears when done
   │   │
   │   └── Input area:
   │       ├── Textarea (auto-expand, max 5 lines)
   │       ├── Send button (← Enter to send, Shift+Enter new line)
   │       └── Usage indicator: "12/50 queries today"
   │
   └── Sidebar phải (collapsible): RAG instance info
       ├── Name, description
       ├── Knowledge Bases being used
       └── Skills available
```

### Flow E: Admin cấp quyền

```
1. Admin vào /admin/graph-rag/instances/[slug]/permissions
2. Thấy table: User | Access Level | Daily Limit | Monthly Tokens | Expires | Actions
3. Nhấn "Cấp quyền" → modal:
   ├── Search user (email/name)
   ├── Access level dropdown
   ├── Daily query limit (number input)
   ├── Monthly token limit (number input)
   ├── Expires at (date picker, optional)
   └── Submit → toast success

4. Quick actions:
   ├── Bulk assign (select multiple users)
   ├── Edit inline
   └── Revoke (confirm dialog)
```

---

## 3. Feature-Based Folder Structure (Frontend)

```
frontend/src/features/
├── graph-rag/
│   ├── api/
│   │   ├── rag-instance.api.ts      # API calls for RAG instances
│   │   ├── knowledge-base.api.ts    # API calls for KBs
│   │   ├── document.api.ts          # API calls for documents
│   │   ├── graph.api.ts             # API calls for knowledge graph
│   │   ├── skill.api.ts             # API calls for skills
│   │   ├── chat.api.ts              # Chat API (sync + SSE stream)
│   │   ├── conversation.api.ts      # Conversation CRUD
│   │   ├── access.api.ts            # Permission management
│   │   └── analytics.api.ts         # Analytics queries
│   │
│   ├── hooks/
│   │   ├── useRAGInstances.ts        # React Query: list instances
│   │   ├── useRAGInstance.ts         # React Query: single instance
│   │   ├── useRAGConfig.ts           # React Query: get/update config
│   │   ├── useKnowledgeBases.ts      # React Query: list KBs
│   │   ├── useDocuments.ts           # React Query: documents + polling
│   │   ├── useKnowledgeGraph.ts      # React Query: graph data
│   │   ├── useGraphVisualization.ts  # React Query: visualization data
│   │   ├── useSkills.ts              # React Query: skills
│   │   ├── useChat.ts               # Chat mutation (sync)
│   │   ├── useChatStream.ts         # SSE streaming hook
│   │   ├── useConversations.ts       # React Query: conversations
│   │   ├── useRAGAccess.ts           # React Query: permissions
│   │   ├── useMyAccess.ts            # React Query: my access check
│   │   └── useRAGAnalytics.ts        # React Query: analytics
│   │
│   ├── components/
│   │   ├── admin/
│   │   │   ├── RAGInstanceForm.tsx         # Create/edit wizard
│   │   │   ├── RAGInstanceCard.tsx         # Card in list view
│   │   │   ├── RAGInstanceTable.tsx        # Table in list view
│   │   │   ├── ConfigEditor.tsx            # Config tuning panel
│   │   │   ├── ConfigSlider.tsx            # Slider for numeric params
│   │   │   ├── ConfigHistory.tsx           # Config change timeline
│   │   │   ├── KBAssignmentPanel.tsx       # Assign KBs to instance
│   │   │   ├── SkillAssignmentPanel.tsx    # Assign skills to instance
│   │   │   ├── PermissionManager.tsx       # Manage user permissions
│   │   │   ├── DocumentUploader.tsx        # Drag & drop upload
│   │   │   ├── DocumentTable.tsx           # Documents list
│   │   │   ├── ChunkPreview.tsx            # Preview document chunks
│   │   │   ├── GraphVisualization.tsx      # D3.js/react-force-graph
│   │   │   ├── EntityDetail.tsx            # Entity sidebar
│   │   │   ├── CommunityList.tsx           # Communities list
│   │   │   ├── SkillForm.tsx               # Create/edit skill
│   │   │   ├── TestQueryPanel.tsx          # Dry run test
│   │   │   └── AnalyticsDashboard.tsx      # Charts + stats
│   │   │
│   │   └── chat/
│   │       ├── ChatInterface.tsx           # Main chat layout
│   │       ├── ChatSidebar.tsx             # Conversation history sidebar
│   │       ├── ChatMessages.tsx            # Message list
│   │       ├── ChatMessage.tsx             # Single message (user/assistant)
│   │       ├── ChatInput.tsx               # Message input + send
│   │       ├── ChatSources.tsx             # Source references expandable
│   │       ├── ChatStreamStatus.tsx        # "Đang tìm kiếm..." status
│   │       ├── ChatFeedback.tsx            # Thumbs up/down
│   │       ├── RAGInstanceSelector.tsx     # Grid of available instances
│   │       └── UsageIndicator.tsx          # "12/50 queries today"
│   │
│   ├── types/
│   │   ├── rag-instance.types.ts
│   │   ├── knowledge-base.types.ts
│   │   ├── document.types.ts
│   │   ├── graph.types.ts
│   │   ├── skill.types.ts
│   │   ├── conversation.types.ts
│   │   ├── chat.types.ts
│   │   ├── access.types.ts
│   │   └── analytics.types.ts
│   │
│   └── utils/
│       ├── config-defaults.ts             # Default config values
│       ├── config-validation.ts           # Config range validation
│       └── stream-parser.ts               # Parse SSE events
```

---

## 4. Shared UI Components Cần Tạo

| Component | Dùng ở đâu |
|---|---|
| `Slider` | Config editor — temperature, top_k, threshold |
| `JsonEditor` | Config JSON view/edit (fallback) |
| `StatusBadge` | Document status, graph status, instance status |
| `DragDropUploader` | Document upload area |
| `MarkdownRenderer` | Chat messages, community summaries |
| `SourceCard` | Chat sources display |
| `Timeline` | Config history |
| `ForceGraph` | Knowledge graph visualization |
| `StatsCard` | Analytics dashboard metrics |
| `LineChart` | Analytics: queries over time |
| `BarChart` | Analytics: top queries, strategy usage |
| `PieChart` | Analytics: satisfaction rate |
| `WizardStepper` | RAG instance creation form |
| `SearchableSelect` | User search (permissions), entity search |
| `InlineEditor` | Quick edit in tables |

---

## 5. UX Considerations

### Chat Interface

| State | Behavior |
|---|---|
| **Loading (initial)** | Skeleton cho conversation list + empty chat area |
| **Empty state** | "Chào bạn! Hãy đặt câu hỏi để bắt đầu." + suggestion chips |
| **Streaming** | Tokens xuất hiện mượt, status bar hiện step hiện tại |
| **Error (API fail)** | Toast error + retry button trên message |
| **Error (quota exceeded)** | Inline warning: "Bạn đã hết quota hôm nay. Liên hệ admin." |
| **Source display** | Collapsed by default, click expand, numbered references in text |
| **Feedback** | Thumbs appear on hover, click → animate + optional comment |
| **Offline** | "Mất kết nối" banner, disable input |

### Admin — RAG Config Editor

| State | Behavior |
|---|---|
| **Loading** | Skeleton cho form |
| **Unsaved changes** | Yellow dot trên tab, "Unsaved changes" banner, prevent navigation |
| **Save success** | Toast: "Config đã lưu" + history panel refresh |
| **Validation error** | Red border + message under field |
| **Reset confirm** | Dialog: "Reset về mặc định? Thay đổi hiện tại sẽ mất." |

### Admin — Knowledge Base / Documents

| State | Behavior |
|---|---|
| **Upload progress** | Progress bar per file, overall progress |
| **Processing** | Animated status badge, auto-refresh (polling 5s) |
| **Process failed** | Red badge + error message expandable, "Retry" button |
| **Empty KB** | "Chưa có tài liệu. Upload hoặc thêm URL để bắt đầu." |
| **Graph not built** | Banner: "Knowledge Graph chưa được xây dựng." + "Build" button |
| **Graph building** | Progress bar + animated node graphics |

### Admin — Graph Visualization

| State | Behavior |
|---|---|
| **Loading** | Skeleton graph area |
| **Interactive** | Zoom, pan, drag nodes, click → detail sidebar |
| **Large graph** | Max 100 nodes default, "Load more" hoặc filter by type |
| **Search** | Search bar → highlight matching node + center camera |
| **Filter** | Checkboxes by entity type (person, org, concept...) |

---

## 6. Key Technical Notes

### SSE Streaming Implementation (Chat)
```typescript
// useChatStream.ts — Custom hook cho Server-Sent Events
const useChatStream = (instanceSlug: string) => {
  // 1. POST to /chat/stream/ with fetch (not XMLHttpRequest)
  // 2. ReadableStream reader
  // 3. Parse SSE events: status, token, sources, done
  // 4. Accumulate tokens into message content
  // 5. Update React state progressively
  // 6. Handle errors, timeouts, reconnection
}
```

### Graph Visualization Library
- **Option A**: `react-force-graph-2d` — Simple, performant, good for <1000 nodes
- **Option B**: `@antv/g6` — Feature-rich, Chinese documentation, good for complex graphs
- **Recommended**: `react-force-graph-2d` cho MVP, migrate nếu cần features phức tạp

### Real-time Document Processing Status
- Polling every 5 seconds khi có documents đang processing
- Switch to WebSocket nếu cần real-time hơn (Phase 5+)

### Config Editor
- Dùng Zod schema để validate config ranges
- Mỗi field có: label, value, default, min, max, step, description
- Show diff khi có changes (old value → new value)
