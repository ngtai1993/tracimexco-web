# 📋 App Contents — Bản Kế Hoạch

## 1. Tổng Quan

| Mục | Mô tả |
|-----|-------|
| **Mục đích** | Quản lý nội dung bài viết đa nền tảng mạng xã hội, tự động tạo nội dung (text + layout banner) bằng RAG, lên lịch đăng bài & webhook tương tác với các platform bên ngoài |
| **Người dùng** | Admin (quản lý toàn bộ), Editor (tạo & duyệt nội dung), Creator (tạo nội dung) |
| **Nền tảng** | Web (Django API + Next.js frontend) |
| **Tích hợp** | App `graph_rag` (tạo nội dung tự động), App `agents` (LLM provider), Celery Beat (lên lịch), Webhook outgoing/incoming |

---

## 2. Danh Sách Tính Năng Đã Lọc

### ✅ Phase 1 — MVP

**📝 Quản Lý Bài Viết**
- ✅ Tạo / chỉnh sửa / xóa bài viết (tiêu đề, nội dung, hashtags, media)
- ✅ Phân loại theo Category (cấu trúc cây) và Tags
- ✅ Quản lý trạng thái: `Draft → Review → Approved → Scheduled → Published → Archived`
- ✅ Gắn nhiều media (ảnh, video) vào 1 bài viết
- ✅ Duplicate bài viết để tạo phiên bản cho nền tảng khác
- ✅ Lưu bài viết dưới dạng template tái sử dụng
- ✅ Version history — lịch sử chỉnh sửa bài viết

**🤖 Tạo Nội Dung Bằng RAG**
- ✅ Tạo nội dung bài viết tự động từ prompt + RAG Instance
- ✅ Tạo nhiều phiên bản nội dung (A/B variants) cho cùng 1 chủ đề
- ✅ Tự động đề xuất hashtags dựa trên nội dung
- ✅ Tóm tắt nội dung dài thành post ngắn cho từng nền tảng
- ✅ Tạo caption cho ảnh/video bằng RAG
- ✅ Dịch nội dung sang ngôn ngữ khác
- ✅ Gợi ý cải thiện nội dung (tone, engagement)

**🎨 Tạo Layout Banner Tự Động**
- ✅ RAG phân tích nội dung → sinh mô tả bố cục banner (JSON schema)
- ✅ Layout bao gồm: tiêu đề, tagline, logo, hình nền, màu sắc, font gợi ý
- ✅ Tạo 2–3 phương án layout cho 1 bài viết
- ✅ Chỉnh sửa layout description trước khi xuất
- ✅ Lưu layout templates đã duyệt để tái sử dụng
- ✅ Kết nối RAG knowledge base chứa brand guidelines

**📅 Lên Lịch Đăng Bài**
- ✅ Lên lịch đăng bài cho từng nền tảng (ngày/giờ cụ thể)
- ✅ Hủy / thay đổi lịch đã lên
- ✅ Retry tự động khi đăng thất bại (exponential backoff)
- ✅ Queue management — xem hàng đợi bài sắp đăng

**🔗 Nền Tảng & Webhook**
- ✅ Quản lý danh sách nền tảng (Facebook Page, Zalo OA, TikTok, LinkedIn, Twitter/X, Custom)
- ✅ Cấu hình webhook URL + secret key cho từng nền tảng (thay thế OAuth2)
- ✅ Webhook outgoing — gửi payload bài viết đến nền tảng khi đến lịch
- ✅ Webhook incoming — nhận callback (đăng thành công, lỗi, engagement)
- ✅ Webhook signature verification (HMAC SHA-256)
- ✅ Webhook logs — ghi nhận mọi request/response
- ✅ Webhook health check — kiểm tra kết nối còn hoạt động

**📊 Analytics**
- ✅ Thống kê bài viết theo trạng thái, nền tảng
- ✅ Báo cáo lịch sử đăng bài (thành công / thất bại)
- ✅ Dashboard tổng quan

**👥 Workflow & Phân Quyền**
- ✅ Role-based: Admin / Editor / Creator
- ✅ Approval flow: Creator → Editor review → Admin approve
- ✅ Comment nội bộ trên bài viết

### 🔜 Phase 2 — Sau MVP
- 🔜 Xem trước bài viết theo format từng nền tảng
- 🔜 Bulk scheduling (lên lịch hàng loạt)
- 🔜 Calendar view — lịch đăng bài trực quan
- 🔜 Gợi ý thời gian đăng tối ưu (dựa trên analytics)
- 🔜 Theo dõi engagement (likes, shares — nếu platform hỗ trợ)
- 🔜 So sánh hiệu quả manual vs. AI-generated
- 🔜 Xuất báo cáo CSV/Excel
- 🔜 Email notification
- 🔜 Audit log chi tiết

### ❌ Không làm
- ❌ Kết nối OAuth2 trực tiếp với nền tảng (dùng webhook + API token thay thế)

---

## 3. Kiến Trúc Hệ Thống

### Django Apps

| App | Domain | Mô tả |
|-----|--------|-------|
| `contents` | Bài viết | Post CRUD, Category, Tag, Media, Version, Template, Banner Layout, AI Generation |
| `platforms` | Nền tảng & Webhook | Platform config, Webhook outgoing/incoming, Webhook log, Health check |
| `scheduling` | Lên lịch | PostSchedule, PublishAttempt, Celery Beat integration, retry queue |

> **Lưu ý:** AI generation gọi qua service của `graph_rag` app — không tạo app mới.

---

### Models Chính & Quan Hệ

```
Category
├── parent → Category (self FK, nullable — cấu trúc cây)
└── có nhiều → Post

Tag
└── có nhiều → Post (M2M qua PostTag)

Post
├── category (FK Category)
├── author (FK User)
├── rag_instance (FK RAGInstance, nullable — dùng để generate)
├── status: draft | review | approved | scheduled | published | archived
├── platform_type: facebook | zalo | tiktok | linkedin | twitter | custom
├── is_ai_generated (bool)
├── có nhiều → PostMedia
├── có nhiều → PostVersion
├── có nhiều → PostTag
├── có nhiều → PostComment
├── có nhiều → BannerLayout
└── có nhiều → PostSchedule (qua scheduling app)

PostMedia
├── post (FK)
├── media_type: image | video | file
├── file (FileField)
├── caption
└── order (int)

PostVersion
├── post (FK)
├── version_number (int)
├── content (text)
└── changed_by (FK User)

PostTemplate
├── name
├── platform_type
├── content_template (text)
└── category (FK, nullable)

PostComment
├── post (FK)
├── author (FK User)
└── content (text — comment nội bộ)

AIContentGeneration
├── post (FK, nullable — có thể generate trước khi tạo post)
├── rag_instance (FK RAGInstance)
├── generation_type: full_post | hashtags | summary | caption | translation | improvement | ab_variant
├── prompt (text)
├── result_content (text)
└── status: pending | processing | completed | failed

BannerLayout
├── post (FK)
├── rag_instance (FK RAGInstance, nullable)
├── variant_index (int — 1, 2, 3)
├── layout_json (JSON) — bố cục đầy đủ
├── is_approved (bool)
└── approved_by (FK User, nullable)

LayoutTemplate
├── name
├── platform_type
├── layout_json (JSON)
└── is_active (bool)
```

```
Platform
├── name, slug
├── platform_type: facebook | zalo | tiktok | linkedin | twitter | custom
├── webhook_url (outgoing — nền tảng nhận bài viết)
├── webhook_secret (signing key cho outgoing)
├── health_status: healthy | degraded | unreachable
└── is_active (bool)

WebhookEndpoint
├── platform (FK)
├── endpoint_url (incoming — URL nhận callback)
├── event_types (JSON array: ["publish_success", "publish_error", "engagement"])
├── secret_key (HMAC SHA-256 verification)
└── is_active (bool)

WebhookLog
├── platform (FK)
├── direction: outgoing | incoming
├── event_type (str)
├── payload (JSON)
├── response_status (int)
├── response_body (text)
└── created_at
```

```
PostSchedule
├── post (FK)
├── platform (FK)
├── scheduled_at (DateTimeField)
├── timezone (str)
└── status: pending | processing | published | failed | cancelled

PublishAttempt
├── schedule (FK PostSchedule)
├── attempt_number (int)
├── attempted_at (DateTimeField)
├── status: success | failed
├── error_message (text)
└── response_data (JSON)
```

---

### Luồng Hoạt Động Chính

**Luồng tạo bài viết với AI:**
```
User nhập prompt + chọn RAG Instance
    ↓
POST /api/contents/ai/generate/
    ↓
[AIGenerationService] → gọi graph_rag PipelineService
    ↓
Lưu AIContentGeneration (status=processing)
    ↓ (async Celery task)
LLM sinh nội dung → lưu result_content (status=completed)
    ↓
User xem kết quả → chọn variant → tạo Post từ nội dung này
```

**Luồng tạo banner layout:**
```
Post đã có nội dung
    ↓
POST /api/contents/posts/<id>/banner-layouts/generate/
    ↓
[BannerLayoutService] → gọi RAG với brand guidelines KB
    ↓
RAG phân tích nội dung + brand guidelines
    ↓
Sinh layout_json: { title_position, tagline, background_color, font, logo_placement, ... }
    ↓
Tạo 2-3 BannerLayout variants
    ↓
User chọn + chỉnh sửa → approve 1 variant
```

**Luồng lên lịch & đăng bài:**
```
Post status = approved
    ↓
POST /api/scheduling/schedules/ (chọn platform + thời gian)
    ↓
Tạo PostSchedule (status=pending)
    ↓
[Celery Beat] quét schedules đến hạn mỗi phút
    ↓
task_publish_post(schedule_id) → gọi WebhookService
    ↓
POST <platform.webhook_url> với payload bài viết + HMAC signature
    ↓
Lưu WebhookLog (outgoing)
    ↓
[Nền tảng xử lý] → gửi callback về WebhookEndpoint
    ↓
POST /api/platforms/incoming/<platform_slug>/
    ↓
Verify HMAC signature → xử lý event
    ↓
Cập nhật PostSchedule status + lưu WebhookLog (incoming)
    ↓
Tạo PublishAttempt record
```

**Luồng approval workflow:**
```
Creator tạo Post (status=draft)
    ↓
Submit review → status=review
    ↓
Editor nhận notification → xem xét
    ↓
Reject → status=draft + comment lý do
Approve → status=approved
    ↓
Admin lên lịch hoặc publish ngay
```

---

## 4. Đặc Tả API

### Nhóm: Taxonomy (Categories & Tags)

---

**GET /api/contents/categories/**
- **Mục đích:** Lấy danh sách categories dạng cây (tree)
- **Permission:** Đã đăng nhập
- **Output:** List categories với `children` lồng nhau, `200 OK`

---

**POST /api/contents/categories/**
- **Mục đích:** Tạo category mới
- **Permission:** Admin
- **Input:**
  - `name` (string, bắt buộc)
  - `slug` (string, tuỳ chọn — tự generate từ name)
  - `parent` (uuid, tuỳ chọn — ID category cha)
  - `description` (string, tuỳ chọn)
- **Output:** `201 Created` — category vừa tạo

---

**PATCH /api/contents/categories/\<slug\>/**
- **Mục đích:** Cập nhật category
- **Permission:** Admin
- **Input:** Các field cần cập nhật (partial update)
- **Output:** `200 OK` — category đã cập nhật
- **Lỗi:** `400` nếu tạo vòng lặp cha-con

---

**DELETE /api/contents/categories/\<slug\>/**
- **Mục đích:** Xóa category (soft delete)
- **Permission:** Admin
- **Logic:** Nếu có children hoặc posts → trả `400` yêu cầu di chuyển trước

---

**GET /api/contents/tags/**
- **Mục đích:** Lấy danh sách tags, hỗ trợ search
- **Permission:** Đã đăng nhập
- **Query params:** `search` (string)

---

**POST /api/contents/tags/**
- **Mục đích:** Tạo tag mới
- **Permission:** Editor, Admin
- **Input:** `name` (string)

---

### Nhóm: Post Management

---

**GET /api/contents/posts/**
- **Mục đích:** Danh sách bài viết, có filter + search + pagination
- **Permission:** Đã đăng nhập (Creator chỉ thấy bài của mình, Editor/Admin thấy tất cả)
- **Query params:** `status`, `platform_type`, `category`, `tags`, `search`, `is_ai_generated`, `page`
- **Output:** Paginated list posts

---

**POST /api/contents/posts/**
- **Mục đích:** Tạo bài viết mới (status mặc định = draft)
- **Permission:** Creator, Editor, Admin
- **Input:**
  - `title` (string, bắt buộc)
  - `content` (string, bắt buộc)
  - `platform_type` (string, bắt buộc)
  - `category` (uuid, tuỳ chọn)
  - `tags` (array of uuid, tuỳ chọn)
  - `hashtags` (array of string, tuỳ chọn)
  - `rag_instance` (uuid, tuỳ chọn — RAG instance đã dùng để generate)
  - `is_ai_generated` (bool, mặc định false)
- **Output:** `201 Created`
- **Logic:**
  1. Tạo Post với status=draft
  2. Tạo PostVersion đầu tiên (version_number=1)

---

**GET /api/contents/posts/\<id\>/**
- **Mục đích:** Chi tiết 1 bài viết kèm media, versions, banner layouts
- **Permission:** Đã đăng nhập + có quyền xem

---

**PATCH /api/contents/posts/\<id\>/**
- **Mục đích:** Cập nhật nội dung bài viết
- **Permission:** Tác giả hoặc Editor/Admin
- **Logic:**
  1. Lưu nội dung cũ vào PostVersion trước khi cập nhật
  2. Tăng version_number

---

**DELETE /api/contents/posts/\<id\>/**
- **Mục đích:** Xóa bài viết (soft delete)
- **Permission:** Admin, hoặc tác giả khi status=draft
- **Lỗi:** `400` nếu bài đang scheduled/published

---

**POST /api/contents/posts/\<id\>/duplicate/**
- **Mục đích:** Nhân bản bài viết (cho nền tảng khác)
- **Permission:** Creator, Editor, Admin
- **Input:** `platform_type` (nền tảng đích)
- **Output:** `201 Created` — post mới với status=draft

---

**POST /api/contents/posts/\<id\>/submit-review/**
- **Mục đích:** Creator nộp bài để Editor review (draft → review)
- **Permission:** Tác giả (Creator)
- **Lỗi:** `400` nếu status không phải draft

---

**POST /api/contents/posts/\<id\>/approve/**
- **Mục đích:** Editor/Admin duyệt bài (review → approved)
- **Permission:** Editor, Admin

---

**POST /api/contents/posts/\<id\>/reject/**
- **Mục đích:** Trả bài về draft kèm lý do
- **Permission:** Editor, Admin
- **Input:** `reason` (string, bắt buộc)
- **Logic:** status → draft, tạo PostComment với nội dung lý do

---

**GET /api/contents/posts/\<id\>/versions/**
- **Mục đích:** Lịch sử chỉnh sửa của bài viết
- **Permission:** Đã đăng nhập + có quyền xem post

---

**POST /api/contents/posts/\<id\>/media/**
- **Mục đích:** Tải media lên gắn với bài viết
- **Permission:** Tác giả, Editor, Admin
- **Input:** `file` (multipart), `media_type`, `caption`, `order`
- **Output:** `201 Created` — media vừa upload

---

**DELETE /api/contents/posts/\<id\>/media/\<media_id\>/**
- **Mục đích:** Xóa media khỏi bài viết
- **Permission:** Tác giả, Editor, Admin

---

**GET /api/contents/posts/\<id\>/comments/**
- **Mục đích:** Lấy danh sách comment nội bộ của bài viết
- **Permission:** Đã đăng nhập + có quyền xem post

---

**POST /api/contents/posts/\<id\>/comments/**
- **Mục đích:** Thêm comment nội bộ
- **Permission:** Đã đăng nhập + có quyền xem post
- **Input:** `content` (string)

---

### Nhóm: AI Content Generation

---

**POST /api/contents/ai/generate/**
- **Mục đích:** Sinh nội dung bài viết từ prompt + RAG instance
- **Permission:** Creator, Editor, Admin
- **Input:**
  - `rag_instance` (uuid, bắt buộc)
  - `prompt` (string, bắt buộc)
  - `platform_type` (string — để điều chỉnh độ dài/format)
  - `variants` (int, mặc định 1, tối đa 3 — số phiên bản A/B)
  - `language` (string, mặc định "vi")
- **Output:** `202 Accepted` — `{ generation_id, status: "processing" }`
- **Logic:**
  1. Tạo AIContentGeneration record (status=processing)
  2. Dispatch Celery task `task_generate_content`
  3. Task gọi graph_rag PipelineService → sinh nội dung
  4. Cập nhật result_content (status=completed)

---

**GET /api/contents/ai/generations/\<id\>/**
- **Mục đích:** Kiểm tra trạng thái + lấy kết quả generation
- **Permission:** Người tạo, Admin
- **Output:** `{ status, result_content, variants[] }`

---

**POST /api/contents/ai/suggest-hashtags/**
- **Mục đích:** Đề xuất hashtags dựa trên nội dung
- **Permission:** Đã đăng nhập
- **Input:** `content` (string), `platform_type`, `count` (int, mặc định 10)
- **Output:** `{ hashtags: ["#tag1", "#tag2", ...] }`

---

**POST /api/contents/ai/summarize/**
- **Mục đích:** Tóm tắt nội dung dài thành post ngắn cho nền tảng
- **Permission:** Đã đăng nhập
- **Input:** `content` (string), `platform_type`, `max_length` (int)

---

**POST /api/contents/ai/translate/**
- **Mục đích:** Dịch nội dung sang ngôn ngữ khác
- **Permission:** Đã đăng nhập
- **Input:** `content` (string), `target_language` (string, vd: "en", "zh")

---

**POST /api/contents/ai/improve/**
- **Mục đích:** Gợi ý cải thiện nội dung (tone, engagement, clarity)
- **Permission:** Đã đăng nhập
- **Input:** `content` (string), `improvement_type`: `tone | engagement | clarity | seo`

---

**POST /api/contents/ai/generate-caption/**
- **Mục đích:** Sinh caption cho ảnh/video đã upload
- **Permission:** Đã đăng nhập
- **Input:** `media_id` (uuid), `rag_instance` (uuid, tuỳ chọn)

---

### Nhóm: Banner Layout

---

**GET /api/contents/posts/\<id\>/banner-layouts/**
- **Mục đích:** Danh sách banner layouts của bài viết
- **Permission:** Đã đăng nhập + có quyền xem post

---

**POST /api/contents/posts/\<id\>/banner-layouts/generate/**
- **Mục đích:** Dùng RAG để sinh layout description cho banner
- **Permission:** Creator, Editor, Admin
- **Input:**
  - `rag_instance` (uuid, tuỳ chọn — nên trỏ đến KB brand guidelines)
  - `variants` (int, mặc định 2)
- **Output:** `202 Accepted` — layout generation task ID
- **Logic:**
  1. RAG đọc nội dung bài viết + brand guidelines KB
  2. Sinh `layout_json` cho mỗi variant — gồm:
     ```json
     {
       "title": "...",
       "tagline": "...",
       "background": { "type": "color|image", "value": "#1A2B3C" },
       "title_position": "top-center|center|bottom-left",
       "font_family": "Inter|Montserrat|Roboto",
       "accent_color": "#FF5733",
       "logo_placement": "top-left|bottom-right|none",
       "layout_style": "minimal|bold|gradient|card"
     }
     ```
  3. Lưu 2–3 BannerLayout records

---

**PATCH /api/contents/posts/\<id\>/banner-layouts/\<layout_id\>/**
- **Mục đích:** Chỉnh sửa layout_json thủ công
- **Permission:** Creator, Editor, Admin
- **Input:** Partial `layout_json` fields

---

**POST /api/contents/posts/\<id\>/banner-layouts/\<layout_id\>/approve/**
- **Mục đích:** Duyệt 1 variant làm layout chính thức
- **Permission:** Editor, Admin
- **Logic:** Set `is_approved=true`, các variant khác `is_approved=false`

---

**GET /api/contents/layout-templates/**
- **Mục đích:** Danh sách layout templates đã lưu
- **Permission:** Đã đăng nhập

---

**POST /api/contents/layout-templates/**
- **Mục đích:** Lưu layout hiện tại thành template
- **Permission:** Editor, Admin
- **Input:** `name`, `platform_type`, `layout_json`

---

### Nhóm: Templates

---

**GET /api/contents/templates/**
- **Mục đích:** Danh sách post templates, lọc theo platform_type
- **Permission:** Đã đăng nhập

---

**POST /api/contents/templates/**
- **Mục đích:** Lưu bài viết hiện tại thành template
- **Permission:** Editor, Admin
- **Input:** `name`, `platform_type`, `content_template`, `category`

---

**POST /api/contents/templates/\<id\>/use/**
- **Mục đích:** Tạo bài viết mới từ template
- **Permission:** Đã đăng nhập
- **Output:** `201 Created` — post mới với status=draft, nội dung từ template

---

### Nhóm: Platforms & Webhook

---

**GET /api/platforms/**
- **Mục đích:** Danh sách nền tảng đã cấu hình
- **Permission:** Admin, Editor

---

**POST /api/platforms/**
- **Mục đích:** Thêm nền tảng mới
- **Permission:** Admin
- **Input:**
  - `name` (string)
  - `platform_type` (string)
  - `webhook_url` (URL — endpoint nền tảng nhận bài viết)
  - `webhook_secret` (string — dùng ký HMAC outgoing request)
- **Output:** `201 Created`

---

**PATCH /api/platforms/\<slug\>/**
- **Mục đích:** Cập nhật cấu hình nền tảng
- **Permission:** Admin

---

**GET /api/platforms/\<slug\>/health/**
- **Mục đích:** Kiểm tra webhook URL còn hoạt động không
- **Permission:** Admin
- **Logic:** Gửi ping request đến `webhook_url` → trả kết quả health_status

---

**GET /api/platforms/\<slug\>/webhooks/**
- **Mục đích:** Danh sách incoming webhook endpoints
- **Permission:** Admin

---

**POST /api/platforms/\<slug\>/webhooks/**
- **Mục đích:** Thêm endpoint nhận callback từ nền tảng
- **Permission:** Admin
- **Input:**
  - `endpoint_url` (URL — nền tảng gửi callback về đây)
  - `event_types` (array: `["publish_success", "publish_error", "engagement"]`)
  - `secret_key` (string — dùng verify chữ ký incoming)

---

**POST /api/platforms/incoming/\<platform_slug\>/**
- **Mục đích:** Nhận callback từ nền tảng bên ngoài (public endpoint)
- **Permission:** Công khai — nhưng phải verify HMAC signature
- **Header:** `X-Webhook-Signature: sha256=<hmac_hex>`
- **Logic:**
  1. Lấy secret_key của platform
  2. Tính HMAC SHA-256 của raw body
  3. So sánh với signature trong header (constant-time compare)
  4. Nếu không khớp → `401 Unauthorized`
  5. Parse event_type → cập nhật PostSchedule status
  6. Lưu WebhookLog (incoming)

---

**GET /api/platforms/\<slug\>/logs/**
- **Mục đích:** Lịch sử webhook (outgoing + incoming) của nền tảng
- **Permission:** Admin
- **Query params:** `direction`, `status`, `date_from`, `date_to`, `page`

---

### Nhóm: Scheduling

---

**GET /api/scheduling/schedules/**
- **Mục đích:** Danh sách lịch đăng bài, lọc theo status/platform/date
- **Permission:** Đã đăng nhập (Creator chỉ thấy bài của mình)
- **Query params:** `status`, `platform`, `from`, `to`, `page`

---

**POST /api/scheduling/schedules/**
- **Mục đích:** Lên lịch đăng 1 bài viết lên 1 nền tảng
- **Permission:** Editor, Admin
- **Input:**
  - `post` (uuid, bắt buộc — phải có status=approved)
  - `platform` (uuid, bắt buộc)
  - `scheduled_at` (ISO datetime, bắt buộc — phải ở tương lai)
  - `timezone` (string, mặc định "Asia/Ho_Chi_Minh")
- **Output:** `201 Created`
- **Lỗi:** `400` nếu post chưa approved, hoặc thời gian trong quá khứ

---

**PATCH /api/scheduling/schedules/\<id\>/**
- **Mục đích:** Đổi thời gian lịch đăng
- **Permission:** Editor, Admin
- **Lỗi:** `400` nếu status không phải pending

---

**POST /api/scheduling/schedules/\<id\>/cancel/**
- **Mục đích:** Hủy lịch đăng (pending → cancelled)
- **Permission:** Editor, Admin

---

**GET /api/scheduling/schedules/\<id\>/attempts/**
- **Mục đích:** Lịch sử các lần thử đăng bài (bao gồm retry)
- **Permission:** Đã đăng nhập + có quyền xem

---

**GET /api/scheduling/queue/**
- **Mục đích:** Danh sách bài viết sắp đăng trong vòng 24h tới
- **Permission:** Editor, Admin

---

### Nhóm: Analytics

---

**GET /api/contents/analytics/summary/**
- **Mục đích:** Số liệu tổng quan
- **Permission:** Editor, Admin
- **Output:** `{ total_posts, by_status: {...}, by_platform: {...}, ai_generated_count, publish_success_rate }`

---

**GET /api/contents/analytics/posts/**
- **Mục đích:** Thống kê bài viết theo thời gian
- **Permission:** Editor, Admin
- **Query params:** `from`, `to`, `group_by`: `day|week|month`

---

**GET /api/contents/analytics/publish-history/**
- **Mục đích:** Lịch sử đăng bài với kết quả (thành công/thất bại)
- **Permission:** Editor, Admin
- **Query params:** `platform`, `from`, `to`, `status`, `page`

---

## 5. Celery Tasks

| Task | Trigger | Mô tả |
|------|---------|-------|
| `task_generate_content(generation_id)` | API call | Gọi RAG pipeline, cập nhật AIContentGeneration |
| `task_generate_banner_layout(post_id, variants)` | API call | Gọi RAG, sinh layout_json, lưu BannerLayout |
| `task_publish_post(schedule_id)` | Celery Beat (mỗi phút) | Gửi webhook outgoing đến platform |
| `task_retry_publish(schedule_id, attempt)` | Auto retry | Exponential backoff: 5m → 15m → 60m |
| `task_webhook_health_check(platform_id)` | Celery Beat (mỗi 15 phút) | Ping webhook URL, cập nhật health_status |
| `task_log_webhook(log_data)` | Fire-and-forget | Lưu WebhookLog không chặn response |

---

## 6. Thiết Kế UX/UI Frontend

### 6.1 Danh Sách Màn Hình (Routes)

| Route | Mô tả | Ai truy cập |
|-------|-------|-------------|
| `/contents` | Dashboard tổng quan (stats + recent posts + queue) | Editor, Admin |
| `/contents/posts` | Danh sách bài viết (filter, search, sort) | Tất cả |
| `/contents/posts/new` | Tạo bài viết mới | Creator, Editor, Admin |
| `/contents/posts/[id]` | Chi tiết & chỉnh sửa bài viết | Tất cả (theo quyền) |
| `/contents/posts/[id]/banner` | Quản lý banner layout của bài viết | Creator, Editor, Admin |
| `/contents/templates` | Danh sách post templates | Editor, Admin |
| `/contents/categories` | Quản lý categories (dạng cây) | Admin |
| `/contents/tags` | Quản lý tags | Editor, Admin |
| `/contents/queue` | Hàng đợi bài sắp đăng | Editor, Admin |
| `/contents/platforms` | Quản lý cấu hình nền tảng | Admin |
| `/contents/platforms/[slug]/logs` | Webhook logs của 1 nền tảng | Admin |
| `/contents/analytics` | Dashboard analytics | Editor, Admin |

---

### 6.2 Luồng Người Dùng (User Flows)

**Tạo bài viết với AI:**
```
/contents/posts/new
  → Click "Tạo bằng AI"
  → Chọn RAG Instance + nhập prompt + chọn platform
  → Click Generate → loading skeleton
  → Hiện kết quả (1-3 variants)
  → Click "Dùng variant này" → nội dung điền vào editor
  → Thêm media (drag-drop) → gắn tags/category → Submit draft
  → Redirect /contents/posts/[id]
```

**Tạo banner layout:**
```
/contents/posts/[id]/banner
  → Click "Tạo Banner"
  → Chọn RAG Instance (KB brand guidelines)
  → Loading → xuất hiện 2-3 card layout preview
  → Mỗi card hiển thị: title, màu sắc, font, layout style dạng visual mock
  → Click "Chỉnh sửa" → form edit JSON fields hiện ra (không cần code)
  → Click "Duyệt" → đánh dấu approved
```

**Lên lịch đăng bài:**
```
/contents/posts/[id]
  → Status badge = approved → nút "Lên Lịch" xuất hiện
  → Click → Modal: chọn Platform + DateTime picker + timezone
  → Submit → hiện trong queue
  
/contents/queue
  → Danh sách cards theo ngày/giờ
  → Mỗi card: post title, platform badge, thời gian, status
  → Click card → xem chi tiết, xem attempt history
  → Click "Hủy" → confirm dialog → remove khỏi queue
```

**Approval workflow:**
```
/contents/posts (Creator view)
  → Thấy bài status=draft → nút "Nộp Review"
  → Click → confirm → status badge đổi thành "Chờ review"

/contents/posts (Editor view)
  → Filter tab "Chờ review" → thấy danh sách
  → Click vào bài → đọc nội dung
  → Nút "Duyệt" hoặc "Trả về" (kèm nhập lý do)
  → Duyệt → status=approved, Creator nhận notification
  → Trả về → Modal nhập lý do → PostComment được tạo
```

---

### 6.3 Shared UI Components

| Component | Dùng ở đâu | Variants |
|-----------|-----------|---------|
| `PostStatusBadge` | Danh sách, chi tiết post | draft / review / approved / scheduled / published / archived |
| `PlatformBadge` | Danh sách, schedule cards | facebook / zalo / tiktok / linkedin / twitter / custom |
| `PostCard` | Danh sách posts | compact / full |
| `AIGenerateModal` | New post, post detail | - |
| `BannerLayoutCard` | Banner page | preview / edit mode |
| `ScheduleModal` | Post detail page | - |
| `WebhookStatusDot` | Platform list, logs | healthy / degraded / unreachable |
| `AttemptTimeline` | Schedule detail | - |
| `ContentEditor` | New post, post detail | Rich text editor |
| `MediaUploadZone` | Post detail, new post | Multi-file drag-drop |
| `CategoryTreeSelect` | Post form | Dropdown với cấu trúc cây |

---

### 6.4 Features Frontend

```
features/
├── contents/
│   ├── posts/
│   │   ├── PostList          — bảng danh sách + filter bar
│   │   ├── PostForm          — form tạo/chỉnh sửa
│   │   ├── PostDetail        — chi tiết + actions theo role
│   │   ├── PostVersionDrawer — lịch sử phiên bản
│   │   ├── PostCommentThread — comment nội bộ
│   │   └── hooks/            — usePosts, usePostDetail, usePostActions
│   ├── ai/
│   │   ├── AIGeneratePanel   — panel sinh nội dung AI
│   │   ├── AIVariantSelector — chọn variant A/B
│   │   ├── AISuggestHashtags — gợi ý hashtags
│   │   └── hooks/            — useAIGenerate, useGenerationStatus
│   ├── banner/
│   │   ├── BannerLayoutGrid  — lưới hiển thị variants
│   │   ├── BannerLayoutEditor— form chỉnh sửa layout JSON
│   │   ├── BannerPreview     — visual preview từ layout_json
│   │   └── hooks/            — useBannerLayouts, useGenerateBanner
│   ├── templates/
│   │   ├── TemplateList
│   │   ├── TemplateCard
│   │   └── hooks/            — useTemplates
│   └── taxonomy/
│       ├── CategoryTree      — quản lý cây category
│       ├── TagManager        — CRUD tags
│       └── hooks/            — useCategories, useTags
├── platforms/
│   ├── PlatformList
│   ├── PlatformForm
│   ├── WebhookLogTable
│   ├── HealthStatusIndicator
│   └── hooks/                — usePlatforms, useWebhookLogs
├── scheduling/
│   ├── ScheduleModal
│   ├── QueueList
│   ├── AttemptHistory
│   └── hooks/                — useSchedules, useQueue
└── analytics/
    ├── SummaryCards
    ├── PostsChart
    ├── PublishHistoryTable
    └── hooks/                — useAnalytics
```

---

### 6.5 UX Considerations

| Tính năng | Loading | Empty | Error | Success |
|-----------|---------|-------|-------|---------|
| Danh sách posts | Skeleton table rows | "Chưa có bài viết — Tạo ngay" + CTA button | Toast lỗi API | — |
| AI Generate | Spinner + "Đang tạo nội dung..." (streaming nếu có) | — | Toast "Tạo thất bại, thử lại" | Hiện variants ngay |
| Banner Generate | Card placeholders + progress text | — | Toast + nút retry | Scroll đến variants mới |
| Upload media | Progress bar per file | — | Inline lỗi per file | Thumbnail xuất hiện ngay (optimistic) |
| Lên lịch | Submit button disabled + spinner | — | Inline error trong modal | Modal đóng + toast "Đã lên lịch" + queue refresh |
| Approve bài | Button loading | — | Toast lỗi | Status badge đổi màu ngay (optimistic) |
| Webhook logs | Skeleton rows | "Chưa có log" | — | — |
| Health check | Spinner icon | — | — | Dot đổi màu |
