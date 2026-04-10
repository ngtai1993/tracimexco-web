# GraphRAG — Đặc Tả API Endpoints

---

## Base URL
```
/api/v1/graph-rag/
```

## Authentication
Tất cả endpoints yêu cầu JWT authentication (`Authorization: Bearer <token>`).

## Permission Legend
- 🔴 **Admin Only** — `is_superuser=True`
- 🟡 **Admin + Manager** — `is_staff=True`
- 🟢 **All Authenticated** — Có quyền truy cập RAG instance (qua RAGAccessPermission hoặc is_public)

---

## 1. RAG Instance Management

### 1.1 List RAG Instances
```
GET /instances/
```
| | |
|---|---|
| **Permission** | 🟢 All Authenticated |
| **Mô tả** | Danh sách RAG instances mà user có quyền truy cập. Admin thấy tất cả. |
| **Query Params** | `?purpose=customer_support&is_active=true&search=keyword&page=1` |
| **Response** |
```json
{
  "results": [
    {
      "id": "uuid",
      "name": "Customer Support Bot",
      "slug": "customer-support-bot",
      "description": "...",
      "purpose": "customer_support",
      "provider": {"slug": "openai", "name": "OpenAI"},
      "agent_config": {"name": "GPT-4o", "model_name": "gpt-4o"},
      "knowledge_bases_count": 3,
      "skills_count": 2,
      "is_active": true,
      "is_public": false,
      "created_by": "admin@example.com",
      "created_at": "2026-04-10T..."
    }
  ],
  "count": 10,
  "next": "...",
  "previous": null
}
```

### 1.2 Create RAG Instance
```
POST /instances/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Mô tả** | Tạo RAG instance mới. Retrieval/Generation config sẽ dùng defaults nếu không cung cấp. |
| **Input** |
```json
{
  "name": "Customer Support Bot",
  "slug": "customer-support-bot",
  "description": "Bot hỗ trợ khách hàng trả lời câu hỏi về sản phẩm",
  "purpose": "customer_support",
  "system_prompt": "Bạn là trợ lý hỗ trợ khách hàng của công ty X. Trả lời dựa trên {context}. Luôn trích dẫn nguồn {sources}. Ngôn ngữ: {language}.",
  "provider_slug": "openai",
  "agent_config_id": "uuid (optional)",
  "retrieval_config": {
    "top_k_vector": 15,
    "search_strategy": "hybrid"
  },
  "generation_config": {
    "temperature": 0.5,
    "tone": "formal"
  },
  "is_public": false
}
```
| **Output** | Full RAGInstance object (201 Created) |
| **Logic** | Merge input config với default config. Validate provider tồn tại và active. |

### 1.3 Get RAG Instance Detail
```
GET /instances/<slug>/
```
| | |
|---|---|
| **Permission** | 🟢 All Authenticated (có quyền) |
| **Mô tả** | Chi tiết RAG instance, bao gồm full config. Admin thấy thêm retrieval_config, generation_config. |
| **Response** |
```json
{
  "id": "uuid",
  "name": "Customer Support Bot",
  "slug": "customer-support-bot",
  "description": "...",
  "purpose": "customer_support",
  "system_prompt": "...",
  "provider": {"slug": "openai", "name": "OpenAI"},
  "agent_config": {"name": "GPT-4o", "model_name": "gpt-4o"},
  "retrieval_config": { "...full config..." },
  "generation_config": { "...full config..." },
  "knowledge_bases": [
    {"id": "uuid", "name": "Product Docs", "slug": "product-docs", "priority": 1}
  ],
  "skills": [
    {"id": "uuid", "name": "Web Search", "slug": "web-search", "is_enabled": true}
  ],
  "stats": {
    "total_conversations": 150,
    "total_queries": 1200,
    "avg_latency_ms": 2300,
    "satisfaction_rate": 0.87
  },
  "is_active": true,
  "is_public": false,
  "created_at": "..."
}
```

### 1.4 Update RAG Instance
```
PATCH /instances/<slug>/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Mô tả** | Cập nhật thông tin hoặc config. Config changes được log vào history. |
| **Input** | Partial update — chỉ gửi fields cần thay đổi |
```json
{
  "retrieval_config": {
    "top_k_vector": 20,
    "reranking_enabled": false
  },
  "generation_config": {
    "temperature": 0.3
  },
  "config_change_reason": "Tăng top_k để bao phủ hơn"
}
```
| **Logic** | Deep merge config (không replace toàn bộ). Log old → new vào RAGConfigHistory. |

### 1.5 Delete RAG Instance
```
DELETE /instances/<slug>/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Mô tả** | Soft delete RAG instance. Conversations giữ nguyên nhưng không chat thêm được. |

### 1.6 Clone RAG Instance
```
POST /instances/<slug>/clone/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Mô tả** | Clone instance (config, KB assignments, skills). Tạo instance mới với tên/slug khác. |
| **Input** |
```json
{
  "name": "Customer Support Bot v2",
  "slug": "customer-support-bot-v2"
}
```

---

## 2. RAG Instance Config Tuning

### 2.1 Get Retrieval Config
```
GET /instances/<slug>/retrieval-config/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Response** | Full retrieval config JSON với default values filled in |

### 2.2 Update Retrieval Config
```
PATCH /instances/<slug>/retrieval-config/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Input** | Partial JSON — chỉ fields cần thay |
| **Logic** | Deep merge. Log history. Validate ranges (e.g., top_k 1-100, threshold 0-1). |

### 2.3 Get Generation Config
```
GET /instances/<slug>/generation-config/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |

### 2.4 Update Generation Config
```
PATCH /instances/<slug>/generation-config/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Logic** | Deep merge. Log history. Validate ranges. |

### 2.5 Get Config History
```
GET /instances/<slug>/config-history/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Query Params** | `?config_type=retrieval&page=1` |
| **Response** |
```json
{
  "results": [
    {
      "id": "uuid",
      "config_type": "retrieval",
      "old_value": {"top_k_vector": 10},
      "new_value": {"top_k_vector": 20},
      "changed_by": "admin@example.com",
      "reason": "Tăng top_k để bao phủ hơn",
      "created_at": "2026-04-10T..."
    }
  ]
}
```

### 2.6 Reset Config to Defaults
```
POST /instances/<slug>/reset-config/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Input** | `{"config_type": "retrieval"}` hoặc `{"config_type": "generation"}` hoặc `{"config_type": "all"}` |
| **Logic** | Reset về default values. Log history. |

---

## 3. Knowledge Base Management

### 3.1 List Knowledge Bases
```
GET /knowledge-bases/
```
| | |
|---|---|
| **Permission** | 🟡 Admin + Manager |
| **Query Params** | `?search=keyword&is_active=true` |
| **Response** |
```json
{
  "results": [
    {
      "id": "uuid",
      "name": "Product Documentation",
      "slug": "product-docs",
      "description": "...",
      "chunk_strategy": "recursive",
      "chunk_size": 512,
      "chunk_overlap": 50,
      "embedding_model": "text-embedding-3-small",
      "document_count": 45,
      "total_chunks": 1200,
      "graph_status": "ready",
      "is_active": true,
      "created_at": "..."
    }
  ]
}
```

### 3.2 Create Knowledge Base
```
POST /knowledge-bases/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Input** |
```json
{
  "name": "Product Documentation",
  "slug": "product-docs",
  "description": "Tài liệu sản phẩm công ty",
  "chunk_strategy": "recursive",
  "chunk_size": 512,
  "chunk_overlap": 50,
  "embedding_model": "text-embedding-3-small"
}
```

### 3.3 Get Knowledge Base Detail
```
GET /knowledge-bases/<slug>/
```
| | |
|---|---|
| **Permission** | 🟡 Admin + Manager |
| **Response** | Full KB info + graph stats + recent documents |

### 3.4 Update Knowledge Base
```
PATCH /knowledge-bases/<slug>/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Note** | Nếu thay đổi chunk_strategy/size/overlap, cần reprocess documents |

### 3.5 Delete Knowledge Base
```
DELETE /knowledge-bases/<slug>/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Logic** | Soft delete. Cascade: documents, chunks, graph. Gỡ khỏi RAG instances. |

### 3.6 Assign KB to RAG Instance
```
POST /instances/<slug>/knowledge-bases/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Input** | `{"knowledge_base_id": "uuid", "priority": 1}` |

### 3.7 Remove KB from RAG Instance
```
DELETE /instances/<slug>/knowledge-bases/<kb_id>/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |

---

## 4. Document Management

### 4.1 List Documents
```
GET /knowledge-bases/<slug>/documents/
```
| | |
|---|---|
| **Permission** | 🟡 Admin + Manager |
| **Query Params** | `?status=completed&source_type=file_upload&search=keyword` |

### 4.2 Upload Document (File)
```
POST /knowledge-bases/<slug>/documents/upload/
```
| | |
|---|---|
| **Permission** | 🟡 Admin + Manager (nếu có quyền use_upload) |
| **Content-Type** | `multipart/form-data` |
| **Input** |
```
file: <binary>
title: "Product Manual v3"
description: "Tài liệu hướng dẫn sử dụng sản phẩm X"
```
| **Logic** | Save file → Tạo Document (status=pending) → Dispatch Celery task `process_document_task` |
| **Response** | 202 Accepted + Document object with status="pending" |

### 4.3 Add Document (Text)
```
POST /knowledge-bases/<slug>/documents/text/
```
| | |
|---|---|
| **Permission** | 🟡 Admin + Manager |
| **Input** |
```json
{
  "title": "FAQ Section",
  "content_text": "Câu hỏi 1: ... Trả lời: ...",
  "description": "Các câu hỏi thường gặp"
}
```

### 4.4 Add Document (URL)
```
POST /knowledge-bases/<slug>/documents/url/
```
| | |
|---|---|
| **Permission** | 🟡 Admin + Manager |
| **Input** |
```json
{
  "title": "Company Blog Post",
  "source_url": "https://example.com/blog/post-1",
  "description": "Bài viết blog về sản phẩm mới"
}
```
| **Logic** | Crawl URL → Extract text → Process |

### 4.5 Get Document Detail
```
GET /knowledge-bases/<slug>/documents/<doc_id>/
```
| | |
|---|---|
| **Permission** | 🟡 Admin + Manager |
| **Response** | Document info + processing status + chunk_count + entity_count |

### 4.6 Delete Document
```
DELETE /knowledge-bases/<slug>/documents/<doc_id>/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Logic** | Soft delete. Remove chunks from vector store. Update graph (remove related entities). |

### 4.7 Reprocess Document
```
POST /knowledge-bases/<slug>/documents/<doc_id>/reprocess/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Mô tả** | Xóa chunks cũ → reprocess (hữu ích khi thay đổi chunk config) |

### 4.8 Preview Chunks
```
GET /knowledge-bases/<slug>/documents/<doc_id>/chunks/
```
| | |
|---|---|
| **Permission** | 🟡 Admin + Manager |
| **Query Params** | `?page=1&page_size=20` |
| **Response** |
```json
{
  "results": [
    {
      "id": "uuid",
      "chunk_index": 0,
      "content": "Đây là nội dung chunk đầu tiên...",
      "token_count": 128,
      "metadata": {"page_number": 1}
    }
  ]
}
```

---

## 5. Knowledge Graph

### 5.1 Get Graph Status
```
GET /knowledge-bases/<slug>/graph/
```
| | |
|---|---|
| **Permission** | 🟡 Admin + Manager |
| **Response** |
```json
{
  "status": "ready",
  "entity_count": 350,
  "relationship_count": 520,
  "community_count": 25,
  "last_built_at": "2026-04-10T...",
  "build_error": null
}
```

### 5.2 Build/Rebuild Knowledge Graph
```
POST /knowledge-bases/<slug>/graph/build/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Input** | `{"rebuild": false}` (true = xóa cũ và build lại) |
| **Logic** | Dispatch Celery task. Return 202 Accepted. |

### 5.3 List Entities
```
GET /knowledge-bases/<slug>/graph/entities/
```
| | |
|---|---|
| **Permission** | 🟡 Admin + Manager |
| **Query Params** | `?type=person&search=keyword&page=1` |
| **Response** |
```json
{
  "results": [
    {
      "id": "uuid",
      "name": "Nguyễn Văn A",
      "entity_type": "person",
      "description": "Giám đốc công ty X",
      "properties": {"title": "CEO"},
      "relationship_count": 12,
      "community": {"id": "uuid", "title": "Ban lãnh đạo"}
    }
  ]
}
```

### 5.4 Get Entity Detail + Relationships
```
GET /knowledge-bases/<slug>/graph/entities/<entity_id>/
```
| | |
|---|---|
| **Permission** | 🟡 Admin + Manager |
| **Response** | Entity + all relationships (incoming + outgoing) + source chunks |

### 5.5 List Communities
```
GET /knowledge-bases/<slug>/graph/communities/
```
| | |
|---|---|
| **Permission** | 🟡 Admin + Manager |
| **Query Params** | `?level=0&page=1` |

### 5.6 Get Community Detail
```
GET /knowledge-bases/<slug>/graph/communities/<community_id>/
```
| | |
|---|---|
| **Permission** | 🟡 Admin + Manager |
| **Response** | Community + summary + all entities + key relationships |

### 5.7 Graph Visualization Data
```
GET /knowledge-bases/<slug>/graph/visualization/
```
| | |
|---|---|
| **Permission** | 🟡 Admin + Manager |
| **Query Params** | `?max_nodes=100&center_entity=uuid&depth=2` |
| **Response** |
```json
{
  "nodes": [
    {"id": "uuid", "name": "...", "type": "person", "size": 12, "community_id": "uuid"}
  ],
  "edges": [
    {"source": "uuid", "target": "uuid", "type": "works_at", "weight": 0.95}
  ],
  "communities": [
    {"id": "uuid", "title": "...", "color": "#FF6B6B"}
  ]
}
```

---

## 6. Skills Management

### 6.1 List Available Skills
```
GET /skills/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Response** | All skills (built-in + custom) |

### 6.2 Create Custom Skill
```
POST /skills/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Input** |
```json
{
  "name": "Company API Lookup",
  "slug": "company-api-lookup",
  "description": "Tra cứu thông tin sản phẩm từ API nội bộ. Dùng khi cần thông tin realtime về giá, tồn kho.",
  "skill_type": "api_call",
  "api_endpoint": "https://internal-api.example.com/products/search",
  "api_method": "GET",
  "api_headers": {"Authorization": "Bearer {{INTERNAL_API_KEY}}"},
  "input_schema": {
    "type": "object",
    "properties": {
      "query": {"type": "string", "description": "Product name or code"}
    },
    "required": ["query"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "products": {"type": "array"}
    }
  },
  "config": {
    "timeout": 10,
    "max_results": 5
  }
}
```

### 6.3 Update Skill
```
PATCH /skills/<slug>/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |

### 6.4 Delete Skill
```
DELETE /skills/<slug>/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |

### 6.5 Assign Skill to RAG Instance
```
POST /instances/<slug>/skills/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Input** |
```json
{
  "skill_id": "uuid",
  "is_enabled": true,
  "config_override": {
    "max_results": 3
  }
}
```

### 6.6 Update Skill Assignment
```
PATCH /instances/<slug>/skills/<skill_id>/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Input** | `{"is_enabled": false}` hoặc `{"config_override": {...}}` |

### 6.7 Remove Skill from Instance
```
DELETE /instances/<slug>/skills/<skill_id>/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |

---

## 7. Chat API (Core User-facing)

### 7.1 Send Message (Sync)
```
POST /instances/<slug>/chat/
```
| | |
|---|---|
| **Permission** | 🟢 All Authenticated (có quyền) |
| **Input** |
```json
{
  "message": "Sản phẩm X có những tính năng gì?",
  "conversation_id": "uuid (optional, null = new conversation)"
}
```
| **Response** |
```json
{
  "conversation_id": "uuid",
  "message": {
    "id": "uuid",
    "role": "assistant",
    "content": "Dựa trên tài liệu, sản phẩm X có các tính năng chính sau:\n\n1. **Tính năng A**: ...\n2. **Tính năng B**: ...\n\n*Nguồn: [Product Manual v3, trang 15]*",
    "sources": [
      {
        "type": "chunk",
        "document_title": "Product Manual v3",
        "content_preview": "...đoạn text liên quan...",
        "score": 0.95,
        "metadata": {"page_number": 15}
      },
      {
        "type": "entity",
        "name": "Sản phẩm X",
        "entity_type": "product",
        "description": "..."
      }
    ],
    "skills_used": [],
    "metadata": {
      "tokens_in": 1500,
      "tokens_out": 350,
      "latency_ms": 2100,
      "retrieval_strategy": "hybrid",
      "model": "gpt-4o"
    }
  }
}
```

### 7.2 Send Message (Streaming SSE)
```
POST /instances/<slug>/chat/stream/
```
| | |
|---|---|
| **Permission** | 🟢 All Authenticated (có quyền) |
| **Content-Type Response** | `text/event-stream` |
| **Input** | Same as 7.1 |
| **SSE Events** |
```
event: status
data: {"step": "analyzing_query", "detail": "Phân tích câu hỏi..."}

event: status
data: {"step": "retrieving", "detail": "Tìm kiếm tài liệu liên quan..."}

event: status
data: {"step": "generating", "detail": "Đang tạo câu trả lời..."}

event: token
data: {"content": "Dựa"}

event: token
data: {"content": " trên"}

event: token
data: {"content": " tài liệu"}

... (streaming tokens)

event: sources
data: [{"type": "chunk", "document_title": "...", "score": 0.95}]

event: skills
data: [{"skill": "web_search", "query": "...", "result_summary": "..."}]

event: done
data: {"message_id": "uuid", "conversation_id": "uuid", "metadata": {"tokens_in": 1500, "tokens_out": 350, "latency_ms": 2100}}
```

### 7.3 Message Feedback
```
POST /instances/<slug>/chat/messages/<message_id>/feedback/
```
| | |
|---|---|
| **Permission** | 🟢 All Authenticated |
| **Input** |
```json
{
  "feedback": "thumbs_up",
  "comment": "Câu trả lời chính xác và đầy đủ"
}
```

---

## 8. Conversation Management

### 8.1 List Conversations
```
GET /instances/<slug>/conversations/
```
| | |
|---|---|
| **Permission** | 🟢 All Authenticated (chỉ thấy conversations của mình) |
| **Query Params** | `?search=keyword&page=1` |

### 8.2 Get Conversation Detail + Messages
```
GET /instances/<slug>/conversations/<conversation_id>/
```
| | |
|---|---|
| **Permission** | 🟢 Owner only (hoặc Admin) |
| **Response** | Conversation info + all messages |

### 8.3 Update Conversation Title
```
PATCH /instances/<slug>/conversations/<conversation_id>/
```
| | |
|---|---|
| **Permission** | 🟢 Owner only |
| **Input** | `{"title": "Hỏi về sản phẩm X"}` |

### 8.4 Delete Conversation
```
DELETE /instances/<slug>/conversations/<conversation_id>/
```
| | |
|---|---|
| **Permission** | 🟢 Owner only (hoặc Admin) |

### 8.5 Export Conversation
```
GET /instances/<slug>/conversations/<conversation_id>/export/
```
| | |
|---|---|
| **Permission** | 🟢 Owner only |
| **Query Params** | `?format=json` hoặc `?format=markdown` |

---

## 9. Access Control

### 9.1 List Permissions for RAG Instance
```
GET /instances/<slug>/permissions/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |

### 9.2 Grant Permission
```
POST /instances/<slug>/permissions/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Input** |
```json
{
  "user_id": "uuid",
  "access_level": "use",
  "daily_query_limit": 50,
  "monthly_token_limit": 500000,
  "expires_at": "2026-12-31T23:59:59Z"
}
```

### 9.3 Update Permission
```
PATCH /instances/<slug>/permissions/<permission_id>/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Input** | Partial update |

### 9.4 Revoke Permission
```
DELETE /instances/<slug>/permissions/<permission_id>/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |

### 9.5 Check My Access
```
GET /instances/<slug>/my-access/
```
| | |
|---|---|
| **Permission** | 🟢 All Authenticated |
| **Response** |
```json
{
  "has_access": true,
  "access_level": "use",
  "daily_query_limit": 50,
  "daily_queries_used": 12,
  "monthly_token_limit": 500000,
  "monthly_tokens_used": 125000,
  "expires_at": null
}
```

---

## 10. Analytics

### 10.1 Instance Analytics
```
GET /instances/<slug>/analytics/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only (hoặc Manager với view_analytics permission) |
| **Query Params** | `?period=7d` (7d, 30d, 90d, custom) `&from=2026-04-01&to=2026-04-10` |
| **Response** |
```json
{
  "period": "7d",
  "total_queries": 856,
  "unique_users": 23,
  "total_tokens_in": 1250000,
  "total_tokens_out": 380000,
  "avg_latency_ms": 2150,
  "satisfaction_rate": 0.87,
  "feedback_count": {"thumbs_up": 120, "thumbs_down": 18},
  "queries_by_day": [
    {"date": "2026-04-10", "count": 142},
    {"date": "2026-04-09", "count": 128}
  ],
  "top_queries": [
    {"query": "tính năng sản phẩm X", "count": 15},
    {"query": "giá sản phẩm Y", "count": 12}
  ],
  "retrieval_strategy_usage": {
    "hybrid": 650,
    "vector": 150,
    "graph": 56
  },
  "skills_usage": {
    "web_search": 45,
    "calculator": 12
  }
}
```

### 10.2 Usage Logs
```
GET /instances/<slug>/analytics/logs/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Query Params** | `?user_id=uuid&feedback=thumbs_down&page=1` |

### 10.3 Global Analytics (All Instances)
```
GET /analytics/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Response** | Aggregated stats across all RAG instances |

---

## 11. Utility APIs

### 11.1 Validate Config
```
POST /utils/validate-config/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Input** | `{"config_type": "retrieval", "config": {...}}` |
| **Response** | `{"valid": true, "warnings": ["top_k_vector=100 may increase latency"]}` |

### 11.2 Test RAG Query (Dry Run)
```
POST /instances/<slug>/test/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Mô tả** | Chạy query nhưng không save conversation/log. Hiển thị chi tiết mỗi step. |
| **Input** |
```json
{
  "message": "Test query here",
  "show_retrieval_details": true,
  "show_reranking_scores": true
}
```
| **Response** | Full pipeline debug info: retrieved chunks, scores, graph results, final context, etc. |

### 11.3 Get Available Models
```
GET /utils/models/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Mô tả** | Danh sách models từ app agents (providers + configs) |

### 11.4 Get Default Configs
```
GET /utils/default-configs/
```
| | |
|---|---|
| **Permission** | 🔴 Admin Only |
| **Response** | `{"retrieval": {...defaults...}, "generation": {...defaults...}, "knowledge_base": {...defaults...}}` |

---

## Summary — Tổng Hợp Endpoints

| Group | Endpoints | Permission |
|---|---|---|
| **RAG Instances** | 6 endpoints | Admin create/update, All read |
| **Config Tuning** | 6 endpoints | Admin only |
| **Knowledge Bases** | 7 endpoints | Admin create, Manager read |
| **Documents** | 8 endpoints | Admin delete, Manager upload/read |
| **Knowledge Graph** | 7 endpoints | Manager+ read, Admin build |
| **Skills** | 7 endpoints | Admin only |
| **Chat** | 3 endpoints | All (with permission) |
| **Conversations** | 5 endpoints | Owner + Admin |
| **Access Control** | 5 endpoints | Admin manage, All check |
| **Analytics** | 3 endpoints | Admin + Manager(view) |
| **Utilities** | 4 endpoints | Admin only |
| **Total** | **~61 endpoints** | |
