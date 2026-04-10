# 📋 Contents — Frontend Plan

## 1. Tổng Quan

| Mục | Mô tả |
|-----|-------|
| **Mục đích** | Giao diện quản lý toàn bộ vòng đời bài viết đa nền tảng: soạn thảo, duyệt, lên lịch, tạo nội dung AI, quản lý banner layout, phân tích hiệu quả |
| **Người dùng** | Admin (toàn quyền), Editor (duyệt bài), Creator (tạo bài) |
| **Base URL API** | `/api/v1/contents/` |
| **Tích hợp** | App `graph_rag` (RAG instances cho AI generation), App `scheduling` (lên lịch đăng bài) |

---

## 2. Danh Sách Tính Năng

### Nhóm A — Quản Lý Bài Viết

| # | Tính năng | Ai dùng |
|---|-----------|---------|
| A1 | Danh sách bài viết — filter theo status, platform, category, search | All |
| A2 | Tạo bài viết mới — form đầy đủ (tiêu đề, nội dung, hashtags, platform, category, tags) | Creator+ |
| A3 | Chỉnh sửa bài viết (chỉ khi `status=draft`) | Author / Admin |
| A4 | Xóa bài viết (chỉ `draft`) | Author / Admin |
| A5 | Duplicate bài viết — chuyển sang nền tảng khác | Creator+ |
| A6 | Nộp bài để review (`draft → review`) | Creator |
| A7 | Approve bài (`review → approved`) | Admin |
| A8 | Reject bài với lý do (`review → draft`) | Admin |
| A9 | Upload / xóa media (ảnh, video) vào bài viết | Creator+ |
| A10 | Xem version history — so sánh nội dung các phiên bản | All |
| A11 | Comment nội bộ trên bài viết | All |

### Nhóm B — AI Content Generation

| # | Tính năng | Ai dùng |
|---|-----------|---------|
| B1 | Tạo nội dung bài viết từ prompt + RAG Instance | Creator+ |
| B2 | Tạo nhiều biến thể A/B (2-5 variants) cùng lúc | Creator+ |
| B3 | Gợi ý hashtags từ nội dung | Creator+ |
| B4 | Tóm tắt nội dung dài thành post ngắn | Creator+ |
| B5 | Dịch bài viết sang ngôn ngữ khác | Creator+ |
| B6 | Gợi ý cải thiện nội dung (tone, engagement) | Creator+ |
| B7 | Tạo caption cho ảnh/video | Creator+ |
| B8 | Polling trạng thái generation (pending → processing → completed/failed) | Creator+ |

### Nhóm C — Banner Layout

| # | Tính năng | Ai dùng |
|---|-----------|---------|
| C1 | Sinh banner layout variants (2-3 phương án) từ RAG | Creator+ |
| C2 | Preview layout JSON dưới dạng visual card | All |
| C3 | Chỉnh sửa layout JSON (title, tagline, màu, font, vị trí logo) | Creator+ |
| C4 | Approve layout đã chọn | Admin |
| C5 | Quản lý Layout Templates (lưu layout đã duyệt để tái sử dụng) | Admin |

### Nhóm D — Template

| # | Tính năng | Ai dùng |
|---|-----------|---------|
| D1 | Danh sách Post Templates — filter theo platform, category | All |
| D2 | Tạo / sửa / xóa Post Template | Admin |
| D3 | Apply template vào form tạo bài | Creator+ |

### Nhóm E — Taxonomy (Category & Tag)

| # | Tính năng | Ai dùng |
|---|-----------|---------|
| E1 | CRUD Categories (hỗ trợ cây cha-con) | Admin |
| E2 | CRUD Tags | Admin |
| E3 | Autocomplete tag khi nhập tên | Creator+ |

### Nhóm F — Analytics (Admin Only)

| # | Tính năng | Ai dùng |
|---|-----------|---------|
| F1 | Summary dashboard: tổng bài, by status, by platform, AI count, publish success rate | Admin |
| F2 | Biểu đồ bài viết theo thời gian (group by day/week/month) | Admin |
| F3 | Lịch sử đăng bài — filter theo platform, status | Admin |

---

## 3. API Endpoints Reference

### Posts

| Method | Endpoint | Mô tả | Permission |
|--------|----------|--------|-----------|
| GET | `/posts/` | Danh sách bài viết (filter: status, platform_type, category, search, is_ai_generated) | Auth |
| POST | `/posts/` | Tạo bài viết mới | Auth |
| GET | `/posts/{id}/` | Chi tiết bài viết | Auth |
| PATCH | `/posts/{id}/` | Cập nhật bài viết | Author / Admin |
| DELETE | `/posts/{id}/` | Xóa bài viết (soft delete, chỉ draft) | Author / Admin |
| POST | `/posts/{id}/duplicate/` | Body: `{platform_type}` — nhân bản bài | Auth |
| POST | `/posts/{id}/submit-review/` | Nộp bài để review | Author |
| POST | `/posts/{id}/approve/` | Duyệt bài | Admin |
| POST | `/posts/{id}/reject/` | Body: `{reason}` — trả về draft | Admin |
| GET | `/posts/{id}/versions/` | Lịch sử phiên bản | Auth |
| GET | `/posts/{id}/media/` | Danh sách media | Auth |
| POST | `/posts/{id}/media/` | Upload media (multipart/form-data) | Auth |
| DELETE | `/posts/{id}/media/{media_id}/` | Xóa media | Auth |
| GET | `/posts/{id}/comments/` | Danh sách comment | Auth |
| POST | `/posts/{id}/comments/` | Thêm comment | Auth |

### Categories & Tags

| Method | Endpoint | Mô tả | Permission |
|--------|----------|--------|-----------|
| GET | `/categories/` | Danh sách categories | Auth |
| POST | `/categories/` | Tạo category | Admin |
| GET | `/categories/{slug}/` | Chi tiết category | Auth |
| PATCH | `/categories/{slug}/` | Cập nhật category | Admin |
| DELETE | `/categories/{slug}/` | Xóa category | Admin |
| GET | `/tags/` | Danh sách tags | Auth |
| POST | `/tags/` | Tạo tag | Admin |

### AI Generation

| Method | Endpoint | Mô tả | Input | Permission |
|--------|----------|--------|-------|-----------|
| POST | `/ai/generate/` | Tạo nội dung bài viết | `{rag_instance, prompt, platform_type, variants, language}` | Auth |
| GET | `/ai/generations/{id}/` | Polling trạng thái/kết quả generation | — | Auth |
| POST | `/ai/suggest-hashtags/` | Gợi ý hashtags | `{content, platform_type, count}` | Auth |
| POST | `/ai/summarize/` | Tóm tắt nội dung | `{content, platform_type, max_length}` | Auth |
| POST | `/ai/translate/` | Dịch nội dung | `{content, target_language}` | Auth |
| POST | `/ai/improve/` | Gợi ý cải thiện | `{content, platform_type, tone}` | Auth |
| POST | `/ai/generate-caption/` | Tạo caption | `{context, platform_type}` | Auth |

### Banner Layouts

| Method | Endpoint | Mô tả | Permission |
|--------|----------|--------|-----------|
| GET | `/posts/{id}/banner-layouts/` | Danh sách layouts của bài | Auth |
| POST | `/posts/{id}/banner-layouts/generate/` | Sinh layout variants từ RAG | Auth |
| PATCH | `/posts/{id}/banner-layouts/{layout_id}/` | Chỉnh sửa layout JSON | Auth |
| POST | `/posts/{id}/banner-layouts/{layout_id}/approve/` | Duyệt layout | Admin |

### Templates & Layout Templates

| Method | Endpoint | Mô tả | Permission |
|--------|----------|--------|-----------|
| GET | `/templates/` | Danh sách post templates | Auth |
| POST | `/templates/` | Tạo post template | Admin |
| POST | `/templates/{id}/use/` | Apply template (trả về content) | Auth |
| GET | `/layout-templates/` | Danh sách layout templates | Auth |
| POST | `/layout-templates/` | Tạo layout template | Admin |

### Analytics

| Method | Endpoint | Mô tả | Permission |
|--------|----------|--------|-----------|
| GET | `/analytics/summary/` | Tổng quan: by status, by platform, AI count | Admin |
| GET | `/analytics/posts/` | Biểu đồ bài viết theo thời gian (`?from=&to=&group_by=day\|week\|month`) | Admin |
| GET | `/analytics/publish-history/` | Lịch sử đăng bài (`?platform=&status=`) | Admin |

---

## 4. Thiết Kế Routes/Pages

### 4.1 Route Map

```
/dashboard/
└── contents/
    ├── (index)                         ← Posts List (tất cả bài viết + filter)
    ├── new                             ← Create Post Form
    ├── review                          ← Review Queue (Admin/Editor)
    ├── analytics                       ← Analytics Dashboard (Admin)
    ├── categories                      ← Category Manager (Admin)
    ├── tags                            ← Tag Manager (Admin)
    ├── templates                       ← Post Template List
    ├── layout-templates                ← Layout Template List (Admin)
    └── [postId]/
        ├── (index)                     ← Post Detail / Edit
        ├── media                       ← Media Manager
        ├── versions                    ← Version History
        ├── banners                     ← Banner Layout Manager
        └── ai                         ← AI Generation Panel
```

### 4.2 Chi Tiết Từng Route

| Route | Page Component | Mô tả | Quyền |
|-------|----------------|--------|-------|
| `/dashboard/contents` | `PostListPage` | Bảng bài viết, filter thanh sidebar, status tabs | All |
| `/dashboard/contents/new` | `CreatePostPage` | Form tạo bài hoàn chỉnh + AI sidebar | Creator+ |
| `/dashboard/contents/review` | `ReviewQueuePage` | Danh sách bài chờ review, action approve/reject inline | Admin/Editor |
| `/dashboard/contents/analytics` | `ContentAnalyticsPage` | Summary cards + line chart + publish history table | Admin |
| `/dashboard/contents/categories` | `CategoryManagerPage` | Tree view + CRUD panel | Admin |
| `/dashboard/contents/tags` | `TagManagerPage` | Tag grid + inline add/delete | Admin |
| `/dashboard/contents/templates` | `PostTemplatePage` | Card grid templates, modal apply | All |
| `/dashboard/contents/layout-templates` | `LayoutTemplatePage` | Card grid templates, modal preview | Admin |
| `/dashboard/contents/[postId]` | `PostDetailPage` | Tab editor: Nội dung / Media / Banner / AI / Versions | Auth |
| `/dashboard/contents/[postId]/media` | (tab trong PostDetailPage) | Drag-reorder media gallery | Auth |
| `/dashboard/contents/[postId]/versions` | (tab trong PostDetailPage) | Timeline versions + diff viewer | Auth |
| `/dashboard/contents/[postId]/banners` | (tab trong PostDetailPage) | Layout variant cards + approve | Auth |
| `/dashboard/contents/[postId]/ai` | (tab trong PostDetailPage) | AI generation panel | Auth |

---

## 5. User Flows

### 5.1 Flow: Tạo bài viết thủ công (Creator)

```
1. Vào /dashboard/contents → Click "Tạo bài viết"
2. Redirect /dashboard/contents/new
3. Điền form:
   - Title (required)
   - Platform (required — dropdown: Facebook, Zalo, TikTok, LinkedIn, Twitter, Custom)
   - Category (optional — searchable dropdown theo cây)
   - Tags (optional — multi-select autocomplete, có nút "+" tạo tag mới)
   - Content (required — Textarea với character counter theo platform)
   - Hashtags (text input hoặc AI suggest)
4. Upload media (drag-drop FileDropzone) → Preview thumbnail gallery
5. Nhấn "Lưu nháp" → POST /posts/ → Redirect /dashboard/contents/[id]
6. Tiếp tục chỉnh sửa → PATCH /posts/[id]/
7. Nhấn "Nộp Review" → POST /posts/[id]/submit-review/ → Status badge đổi → review
   Nếu lỗi (status không phải draft) → Toast error
```

### 5.2 Flow: Tạo nội dung bằng AI (Creator)

```
1. Đang ở /dashboard/contents/new hoặc /dashboard/contents/[id]
2. Click tab "AI" hoặc nút "Tạo bằng AI" trong form
3. AI Panel hiện ra:
   - Chọn RAG Instance (dropdown danh sách instances có quyền)
   - Nhập prompt mô tả chủ đề
   - Chọn platform_type (ảnh hưởng tone/length)
   - Chọn ngôn ngữ (mặc định: Tiếng Việt)
   - Số variants (1-5, mặc định 1)
4. Click "Tạo nội dung" → POST /ai/generate/ → Nhận generation_id
5. Polling GET /ai/generations/[id]/ mỗi 2 giây:
   - pending → Spinner + "Đang chuẩn bị..."
   - processing → Progress bar animated + "AI đang viết..."
   - completed → Hiện kết quả
   - failed → Toast error, cho retry
6. Nếu 1 variant: nút "Chèn vào bài" → fill form content
7. Nếu nhiều variants: Card grid variants, click chọn → "Áp dụng"
8. Tùy chọn thêm:
   - "Gợi ý hashtags" → POST /ai/suggest-hashtags/ → Chip list → click để chọn
   - "Cải thiện" → POST /ai/improve/ → Overlay so sánh trước/sau → Accept/Dismiss
   - "Dịch" → POST /ai/translate/ → Modal chọn ngôn ngữ → Preview kết quả
```

### 5.3 Flow: Duyệt bài (Admin/Editor)

```
1. Vào /dashboard/contents/review
2. Thấy danh sách bài có status=review, sắp xếp theo created_at
3. Click bài → Mở PostDetailPage (read-only với action bar ở top)
4. Đọc nội dung, xem media, xem comment nội bộ
5. Action bar hiện 2 nút:
   a. "Duyệt" → Confirm dialog → POST /posts/[id]/approve/ → Toast success
      → Bài biến khỏi review queue, status đổi → approved
   b. "Trả về" → Modal form nhập lý do → POST /posts/[id]/reject/ → Toast
      → Bài về lại draft, creator được thông báo (qua comment)
6. "Thêm comment" → POST /posts/[id]/comments/ → Comment hiện real-time trong list
```

### 5.4 Flow: Quản lý Banner Layout (Creator + Admin)

```
1. Vào /dashboard/contents/[id] → Tab "Banner"
2. Nếu chưa có layout: Empty state + nút "Sinh banner tự động"
3. Click "Sinh banner" → Modal:
   - Chọn RAG Instance (optional)
   - Số variants (mặc định 2)
   - Submit → POST /posts/[id]/banner-layouts/generate/ → 202 Accepted
4. Polling hoặc refresh sau 3s → GET /posts/[id]/banner-layouts/
5. Hiện card grid variants:
   ┌─────────────────┐  ┌─────────────────┐
   │  Variant #1     │  │  Variant #2     │
   │  [Layout Card]  │  │  [Layout Card]  │
   │  "Bold, Dark"   │  │  "Minimal, Light│
   │  [Chỉnh sửa]   │  │  [Chỉnh sửa]   │
   │  [Duyệt] Admin  │  │  [Duyệt] Admin  │
   └─────────────────┘  └─────────────────┘
6. "Chỉnh sửa" → Mở JSON editor (key-value form hoặc raw JSON toggle)
   - Fields: title, tagline, background.type, background.value, accent_color, font_family, layout_style
   - Preview bên phải cập nhật real-time khi nhập
   - Save → PATCH /posts/[id]/banner-layouts/[layout_id]/
7. "Duyệt" (Admin only) → POST /posts/[id]/banner-layouts/[layout_id]/approve/
   → Layout đổi sang approved badge
```

### 5.5 Flow: Xem Version History (Creator/Admin)

```
1. Vào /dashboard/contents/[id] → Tab "Versions"
2. Danh sách versions dạng timeline (mới nhất trên cùng):
   v3 — Chỉnh sửa bởi Nguyen Van A — 10/04/2026 14:30
   v2 — Chỉnh sửa bởi Tran Thi B — 10/04/2026 10:00
   v1 — Tạo bởi Nguyen Van A — 09/04/2026 08:00
3. Click version → Panel bên phải hiện nội dung phiên bản đó (read-only)
4. Nút "So sánh với hiện tại" → Diff view (highlight thêm/bớt)
5. Admin: "Khôi phục phiên bản này" → Confirm → Tạo version mới từ nội dung cũ
```

### 5.6 Flow: Category Manager (Admin)

```
1. Vào /dashboard/contents/categories
2. Bên trái: Tree view (expand/collapse cha-con)
   ├── Marketing (3 bài)
   │   ├── Social Media (10 bài)
   │   └── Email (5 bài)
   └── Sản phẩm (8 bài)
3. Click category → Panel bên phải hiện form edit (name, slug, parent, description, order)
4. Nút "+" → Form tạo category mới (có dropdown chọn cha)
5. Drag để thay đổi order
6. Nút xóa → Confirm dialog (cảnh báo nếu có bài viết/con)
```

### 5.7 Flow: Analytics Dashboard (Admin)

```
1. Vào /dashboard/contents/analytics
2. Row 1 — Summary Cards (từ GET /analytics/summary/):
   [Tổng bài: 142] [Draft: 23] [Published: 87] [AI Generated: 45 (32%)] [Success Rate: 94.2%]
3. Row 2 — Line Chart "Bài viết theo thời gian":
   - Date range picker (7 ngày, 30 ngày, 90 ngày, custom)
   - Group by toggle: Ngày / Tuần / Tháng
   - Dữ liệu từ GET /analytics/posts/?from=&to=&group_by=
4. Row 3 — Donut Charts:
   - Phân bổ theo Platform
   - Phân bổ theo Status
5. Row 4 — Publish History Table (từ GET /analytics/publish-history/):
   | Bài viết | Platform | Lịch đăng | Status | Thời điểm |
   Filter: Platform, Status
```

---

## 6. TypeScript Types

```typescript
// types/contents.ts

export type PostStatus = 'draft' | 'review' | 'approved' | 'scheduled' | 'published' | 'archived'
export type PlatformType = 'facebook' | 'zalo' | 'tiktok' | 'linkedin' | 'twitter' | 'custom'
export type MediaType = 'image' | 'video' | 'file'
export type GenerationStatus = 'pending' | 'processing' | 'completed' | 'failed'
export type GenerationType = 'full_post' | 'hashtags' | 'summary' | 'caption' | 'translation' | 'improvement' | 'ab_variant'

// ── Post ──────────────────────────────────────────────────────
export interface Post {
  id: string
  title: string
  status: PostStatus
  platform_type: PlatformType
  author_name: string
  category_name: string | null
  tags: { id: string; name: string }[]
  is_ai_generated: boolean
  created_at: string
  updated_at: string
}

export interface PostDetail extends Post {
  content: string
  hashtags: string[]
  category: { id: string; name: string; slug: string } | null
  media: PostMedia[]
}

export interface PostInput {
  title: string
  content: string
  hashtags?: string[]
  platform_type: PlatformType
  category?: string | null       // category id
  tags?: string[]                // tag ids
  rag_instance?: string | null
  is_ai_generated?: boolean
}

// ── Media ─────────────────────────────────────────────────────
export interface PostMedia {
  id: string
  media_type: MediaType
  file: string
  file_url: string | null
  caption: string
  order: number
  created_at: string
}

// ── Version ───────────────────────────────────────────────────
export interface PostVersion {
  id: string
  version_number: number
  title: string
  content: string
  changed_by_name: string | null
  created_at: string
}

// ── Comment ───────────────────────────────────────────────────
export interface PostComment {
  id: string
  author_name: string
  content: string
  created_at: string
}

// ── Category ──────────────────────────────────────────────────
export interface Category {
  id: string
  name: string
  slug: string
  parent: string | null         // parent id
  description: string
  order: number
}

// ── Tag ───────────────────────────────────────────────────────
export interface Tag {
  id: string
  name: string
  slug: string
}

// ── AI Generation ─────────────────────────────────────────────
export interface AIGeneration {
  id: string
  generation_type: GenerationType
  prompt: string
  status: GenerationStatus
  result_content: string
  result_variants: string[]
  error_message: string
  created_at: string
}

export interface AIGenerateInput {
  rag_instance: string
  prompt: string
  platform_type?: PlatformType
  variants?: number              // 1-5
  language?: 'vi' | 'en'
}

// ── Banner Layout ─────────────────────────────────────────────
export interface BannerLayoutJson {
  title?: string
  tagline?: string
  background?: { type: 'color' | 'gradient' | 'image'; value: string }
  title_position?: 'top-center' | 'center' | 'bottom-left'
  font_family?: string
  accent_color?: string
  logo_placement?: 'top-left' | 'top-right' | 'none'
  layout_style?: 'bold' | 'minimal' | 'elegant' | 'playful'
}

export interface BannerLayout {
  id: string
  variant_index: number
  layout_json: BannerLayoutJson
  is_approved: boolean
  approved_by?: string | null
}

// ── Templates ─────────────────────────────────────────────────
export interface PostTemplate {
  id: string
  name: string
  platform_type: PlatformType
  content_template: string
  category: string | null
  is_active: boolean
}

export interface LayoutTemplate {
  id: string
  name: string
  platform_type: PlatformType | ''
  layout_json: BannerLayoutJson
  is_active: boolean
}

// ── Analytics ─────────────────────────────────────────────────
export interface AnalyticsSummary {
  total_posts: number
  by_status: Record<PostStatus, number>
  by_platform: Record<PlatformType, number>
  ai_generated_count: number
  publish_success_rate: number | null
}

export interface AnalyticsDataPoint {
  period: string
  count: number
}
```

---

## 7. API Layer (`features/contents/api.ts`)

```typescript
import { apiClient } from '@/lib/api'
import type { ApiResponse, PaginatedResponse } from '@/types/api'
import type { ... } from './types'

const BASE = '/api/v1/contents'

export const contentsApi = {
  // ── Posts ──────────────────────────────────────────
  listPosts: (params?: {
    status?: PostStatus
    platform_type?: PlatformType
    category?: string
    search?: string
    is_ai_generated?: boolean
    page?: number
  }) => apiClient.get<PaginatedResponse<Post>>(`${BASE}/posts/`, { params }),

  getPost: (id: string) =>
    apiClient.get<ApiResponse<PostDetail>>(`${BASE}/posts/${id}/`),

  createPost: (data: PostInput) =>
    apiClient.post<ApiResponse<PostDetail>>(`${BASE}/posts/`, data),

  updatePost: (id: string, data: Partial<PostInput>) =>
    apiClient.patch<ApiResponse<PostDetail>>(`${BASE}/posts/${id}/`, data),

  deletePost: (id: string) =>
    apiClient.delete(`${BASE}/posts/${id}/`),

  duplicatePost: (id: string, platform_type: PlatformType) =>
    apiClient.post<ApiResponse<PostDetail>>(`${BASE}/posts/${id}/duplicate/`, { platform_type }),

  submitReview: (id: string) =>
    apiClient.post<ApiResponse<PostDetail>>(`${BASE}/posts/${id}/submit-review/`),

  approvePost: (id: string) =>
    apiClient.post<ApiResponse<PostDetail>>(`${BASE}/posts/${id}/approve/`),

  rejectPost: (id: string, reason: string) =>
    apiClient.post<ApiResponse<PostDetail>>(`${BASE}/posts/${id}/reject/`, { reason }),

  // ── Media ──────────────────────────────────────────
  listMedia: (postId: string) =>
    apiClient.get<ApiResponse<PostMedia[]>>(`${BASE}/posts/${postId}/media/`),

  uploadMedia: (postId: string, formData: FormData) =>
    apiClient.post<ApiResponse<PostMedia>>(`${BASE}/posts/${postId}/media/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  deleteMedia: (postId: string, mediaId: string) =>
    apiClient.delete(`${BASE}/posts/${postId}/media/${mediaId}/`),

  // ── Versions & Comments ────────────────────────────
  listVersions: (postId: string) =>
    apiClient.get<ApiResponse<PostVersion[]>>(`${BASE}/posts/${postId}/versions/`),

  listComments: (postId: string) =>
    apiClient.get<ApiResponse<PostComment[]>>(`${BASE}/posts/${postId}/comments/`),

  addComment: (postId: string, content: string) =>
    apiClient.post<ApiResponse<PostComment>>(`${BASE}/posts/${postId}/comments/`, { content }),

  // ── Taxonomy ──────────────────────────────────────
  listCategories: () =>
    apiClient.get<ApiResponse<Category[]>>(`${BASE}/categories/`),

  createCategory: (data: Partial<Category>) =>
    apiClient.post<ApiResponse<Category>>(`${BASE}/categories/`, data),

  updateCategory: (slug: string, data: Partial<Category>) =>
    apiClient.patch<ApiResponse<Category>>(`${BASE}/categories/${slug}/`, data),

  deleteCategory: (slug: string) =>
    apiClient.delete(`${BASE}/categories/${slug}/`),

  listTags: () =>
    apiClient.get<ApiResponse<Tag[]>>(`${BASE}/tags/`),

  createTag: (name: string) =>
    apiClient.post<ApiResponse<Tag>>(`${BASE}/tags/`, { name }),

  // ── AI Generation ──────────────────────────────────
  generateContent: (data: AIGenerateInput) =>
    apiClient.post<ApiResponse<{ generation_id: string; status: GenerationStatus }>>(`${BASE}/ai/generate/`, data),

  pollGeneration: (id: string) =>
    apiClient.get<ApiResponse<AIGeneration>>(`${BASE}/ai/generations/${id}/`),

  suggestHashtags: (content: string, platform_type?: PlatformType, count?: number) =>
    apiClient.post<ApiResponse<{ hashtags: string[] }>>(`${BASE}/ai/suggest-hashtags/`, { content, platform_type, count }),

  summarize: (content: string, platform_type?: PlatformType) =>
    apiClient.post<ApiResponse<{ summary: string }>>(`${BASE}/ai/summarize/`, { content, platform_type }),

  translate: (content: string, target_language: string) =>
    apiClient.post<ApiResponse<{ translated: string }>>(`${BASE}/ai/translate/`, { content, target_language }),

  improve: (content: string, platform_type?: PlatformType, tone?: string) =>
    apiClient.post<ApiResponse<{ improved: string }>>(`${BASE}/ai/improve/`, { content, platform_type, tone }),

  generateCaption: (context: string, platform_type?: PlatformType) =>
    apiClient.post<ApiResponse<{ caption: string }>>(`${BASE}/ai/generate-caption/`, { context, platform_type }),

  // ── Banner Layouts ─────────────────────────────────
  listBannerLayouts: (postId: string) =>
    apiClient.get<ApiResponse<BannerLayout[]>>(`${BASE}/posts/${postId}/banner-layouts/`),

  generateBannerLayouts: (postId: string, data: { rag_instance?: string; variants?: number }) =>
    apiClient.post(`${BASE}/posts/${postId}/banner-layouts/generate/`, data),

  updateBannerLayout: (postId: string, layoutId: string, layout_json: BannerLayoutJson) =>
    apiClient.patch<ApiResponse<BannerLayout>>(`${BASE}/posts/${postId}/banner-layouts/${layoutId}/`, { layout_json }),

  approveBannerLayout: (postId: string, layoutId: string) =>
    apiClient.post<ApiResponse<BannerLayout>>(`${BASE}/posts/${postId}/banner-layouts/${layoutId}/approve/`),

  // ── Templates ─────────────────────────────────────
  listPostTemplates: () =>
    apiClient.get<ApiResponse<PostTemplate[]>>(`${BASE}/templates/`),

  usePostTemplate: (id: string) =>
    apiClient.post<ApiResponse<{ content: string }>>(`${BASE}/templates/${id}/use/`),

  listLayoutTemplates: () =>
    apiClient.get<ApiResponse<LayoutTemplate[]>>(`${BASE}/layout-templates/`),

  // ── Analytics ─────────────────────────────────────
  getAnalyticsSummary: () =>
    apiClient.get<ApiResponse<AnalyticsSummary>>(`${BASE}/analytics/summary/`),

  getAnalyticsPosts: (params: { from?: string; to?: string; group_by?: 'day' | 'week' | 'month' }) =>
    apiClient.get<ApiResponse<AnalyticsDataPoint[]>>(`${BASE}/analytics/posts/`, { params }),

  getPublishHistory: (params?: { platform?: string; status?: string; page?: number }) =>
    apiClient.get<PaginatedResponse<unknown>>(`${BASE}/analytics/publish-history/`, { params }),
}
```

---

## 8. Custom Hooks (`features/contents/hooks.ts`)

```typescript
// Danh sách hooks cần viết

// Posts
usePosts(filters)            → { posts, isLoading, pagination }
usePost(id)                  → { post, isLoading }
useCreatePost()              → { createPost, isLoading }
useUpdatePost(id)            → { updatePost, isLoading }
useDeletePost()              → { deletePost }
useDuplicatePost()           → { duplicatePost }
useSubmitReview(id)          → { submit, isLoading }
useApprovePost(id)           → { approve, isLoading }
useRejectPost(id)            → { reject, isLoading }

// Media
usePostMedia(postId)         → { media, upload, remove, reorder, isUploading }

// Versions & Comments
useVersions(postId)          → { versions, isLoading }
useComments(postId)          → { comments, addComment, isLoading }

// Taxonomy
useCategories()              → { categories, categoryTree }   // memoize tree structure
useTags()                    → { tags, create, remove }

// AI Generation
useAIGenerate()              → { generate, generation, isGenerating, pollStatus }
// polling logic: setInterval every 2s while status=pending|processing

// Banner
useBannerLayouts(postId)     → { layouts, generate, update, approve }

// Templates
usePostTemplates()           → { templates, useTemplate }
useLayoutTemplates()         → { templates }

// Analytics
useAnalyticsSummary()        → { summary, isLoading }
useAnalyticsPosts(params)    → { dataPoints, isLoading }
usePublishHistory(params)    → { history, pagination, isLoading }
```

---

## 9. Feature Folder Structure

```
features/
└── contents/
    ├── index.ts                        ← Re-export chính
    ├── api.ts                          ← API functions
    ├── hooks.ts                        ← Custom hooks
    ├── types.ts                        ← TypeScript types
    ├── constants.ts                    ← STATUS_LABELS, PLATFORM_OPTIONS, màu badge
    │
    ├── components/
    │   ├── post/
    │   │   ├── PostTable.tsx           ← Bảng danh sách bài (với filter bar)
    │   │   ├── PostFilterBar.tsx       ← Filter: status tabs + platform + search
    │   │   ├── PostStatusBadge.tsx     ← Badge màu theo status
    │   │   ├── PostCard.tsx            ← Card view (dùng ở template select)
    │   │   ├── PostForm.tsx            ← Form tạo/sửa bài (title, content, platform, tags...)
    │   │   ├── PostActionBar.tsx       ← Thanh action (Submit Review / Approve / Reject)
    │   │   ├── PostDetailTabs.tsx      ← Tab container (Nội dung / Media / Banner / AI / Versions)
    │   │   ├── DuplicatePostModal.tsx  ← Modal chọn platform khi duplicate
    │   │   └── RejectPostModal.tsx     ← Modal nhập lý do từ chối
    │   │
    │   ├── media/
    │   │   ├── MediaGallery.tsx        ← Grid ảnh/video có drag-reorder
    │   │   ├── MediaUploadZone.tsx     ← FileDropzone + preview + progress
    │   │   └── MediaCard.tsx           ← Thumbnail card với nút xóa
    │   │
    │   ├── versions/
    │   │   ├── VersionTimeline.tsx     ← Timeline list versions bên trái
    │   │   └── VersionDiffViewer.tsx   ← Side-by-side diff hiện tại vs version cũ
    │   │
    │   ├── comments/
    │   │   └── PostCommentSection.tsx  ← List comments + form nhập comment mới
    │   │
    │   ├── ai/
    │   │   ├── AIGenerationPanel.tsx   ← Panel chính AI (prompt, settings, result)
    │   │   ├── AIVariantCards.tsx      ← Card grid hiện A/B variants
    │   │   ├── AIGenerationStatus.tsx  ← Loading/pending/processing indicator
    │   │   ├── HashtagSuggestions.tsx  ← Chip list hashtags để click chọn
    │   │   ├── AIImprovePreview.tsx    ← So sánh trước/sau cải thiện
    │   │   └── AITranslateModal.tsx    ← Modal dịch + preview kết quả
    │   │
    │   ├── banner/
    │   │   ├── BannerLayoutGrid.tsx    ← Grid variants banner
    │   │   ├── BannerLayoutCard.tsx    ← Card preview layout (visual)
    │   │   ├── BannerLayoutEditor.tsx  ← Form chỉnh sửa layout JSON key-value
    │   │   ├── BannerPreview.tsx       ← Preview visual banner từ layout JSON
    │   │   └── GenerateBannerModal.tsx ← Modal chọn RAG + số variants
    │   │
    │   ├── taxonomy/
    │   │   ├── CategoryTree.tsx        ← Tree view categories (expand/collapse)
    │   │   ├── CategoryForm.tsx        ← Form CRUD category
    │   │   ├── TagGrid.tsx             ← Grid chips + add/delete
    │   │   └── TagAutocomplete.tsx     ← Multi-select tag với search realtime
    │   │
    │   ├── template/
    │   │   ├── PostTemplateGrid.tsx    ← Card grid post templates
    │   │   ├── PostTemplateCard.tsx    ← Card hiện name, platform, preview
    │   │   ├── LayoutTemplateGrid.tsx  ← Card grid layout templates
    │   │   └── LayoutTemplateCard.tsx  ← Card hiện preview layout JSON
    │   │
    │   └── analytics/
    │       ├── AnalyticsSummaryCards.tsx   ← Row summary cards
    │       ├── PostsOverTimeChart.tsx      ← Line chart + date range picker
    │       ├── PlatformDistributionChart.tsx ← Donut chart by platform
    │       ├── StatusDistributionChart.tsx   ← Donut chart by status
    │       └── PublishHistoryTable.tsx      ← Table lịch sử đăng bài
    │
    └── pages/ (nếu dùng page-level components, tuỳ architecture)
        ├── PostListPage.tsx
        ├── CreatePostPage.tsx
        ├── PostDetailPage.tsx
        ├── ReviewQueuePage.tsx
        ├── ContentAnalyticsPage.tsx
        ├── CategoryManagerPage.tsx
        ├── TagManagerPage.tsx
        ├── PostTemplatePage.tsx
        └── LayoutTemplatePage.tsx
```

---

## 10. Shared UI Components Tái Sử Dụng

Components này đã có trong `components/ui/` — **không cần tạo mới**:

| Component | Dùng ở đâu trong Contents |
|-----------|--------------------------|
| `Badge` | PostStatusBadge, platform badge |
| `StatusBadge` | Hiển thị trạng thái AI generation |
| `Button` | Form actions, approve/reject, generate |
| `Modal` | DuplicatePostModal, RejectPostModal, GenerateBannerModal, AITranslateModal |
| `ConfirmDialog` | Xóa bài, xóa media, xóa category |
| `Input` / `Textarea` | PostForm, CategoryForm, CommentInput |
| `Select` | Platform dropdown, category select, group_by select |
| `FileDropzone` | MediaUploadZone |
| `Skeleton` | Loading state PostTable, PostDetailTabs |
| `Spinner` | AI generation pending |
| `EmptyState` | Post list trống, no banner layouts, no media |
| `Toast` | Thông báo thành công/thất bại mọi action |
| `Tabs` | PostDetailTabs |
| `Avatar` | Author trong PostTable, comment list |

**Cần tạo thêm (chưa có):**

| Component | File | Mô tả |
|-----------|------|--------|
| `CharacterCounter` | `components/ui/CharacterCounter.tsx` | Đếm ký tự textarea theo limit từng platform |
| `DiffViewer` | `components/ui/DiffViewer.tsx` | Side-by-side text diff (dùng cho VersionDiffViewer) |
| `JsonEditor` | `components/ui/JsonEditor.tsx` | Key-value editor cho JSON đơn giản (BannerLayoutEditor) |
| `DateRangePicker` | `components/ui/DateRangePicker.tsx` | Chọn khoảng ngày (analytics) |
| `LineChart` | `components/ui/LineChart.tsx` | Wrap Recharts LineChart (analytics) |
| `DonutChart` | `components/ui/DonutChart.tsx` | Wrap Recharts PieChart (analytics) |
| `HashtagInput` | `components/ui/HashtagInput.tsx` | Input nhập hashtag dạng chips (# prefix auto) |
| `ProgressBar` | `components/ui/ProgressBar.tsx` | Progress animated dùng cho AI generation |

---

## 11. UX Considerations

### 11.1 Character Limits Theo Platform

```
Facebook:  63.206 ký tự  → Warning khi > 60.000
Instagram: 2.200 ký tự   → Warning khi > 2.000
TikTok:    2.200 ký tự   → Warning khi > 2.000
LinkedIn:  3.000 ký tự   → Warning khi > 2.800
Twitter/X: 280 ký tự     → Counter bắt đầu đếm ngược khi < 50 còn lại
```

### 11.2 Status Transitions & Button States

| Current Status | Hiện nút | Ẩn nút |
|----------------|----------|---------|
| `draft` | Lưu nháp, Nộp Review | Approve, Reject |
| `review` | Xem (readonly), Approve (Admin), Reject (Admin) | Lưu nháp, Nộp Review |
| `approved` | Lên lịch (link sang scheduling) | Sửa, Nộp Review |
| `scheduled` | Xem lịch, Hủy lịch (link sang scheduling) | Sửa |
| `published` | Duplicate, Archive | Sửa, Xóa |
| `archived` | Duplicate | Tất cả actions |

### 11.3 Loading States

| Tình huống | Loading UI |
|-----------|------------|
| Post list đang tải | Skeleton rows (5 rows × 6 cells) |
| Post detail đang tải | Skeleton form toàn trang |
| Media uploading | Progress bar per file + thumbnail placeholder |
| AI generating | Animated gradient card + text "AI đang viết..." |
| Banner generating | Skeleton cards 2x + "Đang tạo layout..." |
| Analytics đang tải | Skeleton summary cards + chart placeholder |

### 11.4 Empty States

| Tình huống | Empty State Message |
|-----------|-------------------|
| Không có bài viết | "Chưa có bài viết nào. [Tạo bài viết đầu tiên →]" |
| Review queue trống | "Không có bài nào chờ duyệt. Bạn có thể nghỉ ngơi! ☕" |
| Không có media | "Chưa có ảnh/video. Kéo thả file vào đây để tải lên." |
| Không có banner | "Chưa có banner layout. [Sinh banner tự động →]" |
| Chưa có versions | "Đây là phiên bản đầu tiên." |
| Tags trống | "Chưa có tag nào. [Thêm tag đầu tiên →]" |

### 11.5 Error Handling

| Lỗi | Hiển thị ở đâu |
|-----|----------------|
| Validation form (title, platform...) | Inline dưới field, màu đỏ |
| 403 Forbidden | Toast "Bạn không có quyền thực hiện thao tác này." |
| 404 Not Found | Redirect về list + Toast "Bài viết không tồn tại." |
| 400 Invalid status transition | Toast warning với message từ API |
| Network error | Toast "Mất kết nối. Vui lòng thử lại." + retry button |
| AI generation failed | Toast error + nút "Thử lại" trong AI panel |
| Upload failed | Error message per file trong MediaUploadZone |

### 11.6 Optimistic Updates

| Action | Optimistic |
|--------|-----------|
| Thêm comment | Thêm comment vào list ngay, rollback nếu lỗi |
| Toggle tag selection | Cập nhật chips ngay |
| Xóa media | Xóa khỏi gallery ngay, rollback nếu lỗi |
| Thêm hashtag từ AI suggestion | Thêm ngay vào hashtags field |

### 11.7 Auto-save Draft

- Khi đang ở `/dashboard/contents/new` hoặc `/dashboard/contents/[id]` (chỉ draft):
  - Sau **3 giây dừng nhập** → tự động gọi PATCH /posts/[id]/
  - Hiện indicator nhỏ "Đã lưu tự động" hoặc "Đang lưu..." bên cạnh nút
  - Không auto-save khi status ≠ draft

---

## 12. Platform Character Limit Constants

```typescript
// features/contents/constants.ts

export const PLATFORM_CHAR_LIMITS: Record<PlatformType, number> = {
  facebook: 63206,
  zalo: 5000,
  tiktok: 2200,
  linkedin: 3000,
  twitter: 280,
  custom: Infinity,
}

export const PLATFORM_LABELS: Record<PlatformType, string> = {
  facebook: 'Facebook',
  zalo: 'Zalo',
  tiktok: 'TikTok',
  linkedin: 'LinkedIn',
  twitter: 'Twitter/X',
  custom: 'Custom',
}

export const STATUS_LABELS: Record<PostStatus, string> = {
  draft: 'Nháp',
  review: 'Chờ duyệt',
  approved: 'Đã duyệt',
  scheduled: 'Đã lên lịch',
  published: 'Đã đăng',
  archived: 'Lưu trữ',
}

export const STATUS_COLORS: Record<PostStatus, string> = {
  draft: 'gray',
  review: 'yellow',
  approved: 'blue',
  scheduled: 'purple',
  published: 'green',
  archived: 'red',
}

export const PLATFORM_ICONS: Record<PlatformType, string> = {
  facebook: '📘',
  zalo: '💬',
  tiktok: '🎵',
  linkedin: '💼',
  twitter: '🐦',
  custom: '🌐',
}
```

---

## 13. App Router Structure (Next.js)

```
app/(main)/
└── contents/
    ├── layout.tsx                      ← Sidebar navigation: Posts / Review / Analytics / Categories / Tags / Templates
    ├── page.tsx                        ← PostListPage
    ├── new/
    │   └── page.tsx                    ← CreatePostPage
    ├── review/
    │   └── page.tsx                    ← ReviewQueuePage (Admin/Editor only)
    ├── analytics/
    │   └── page.tsx                    ← ContentAnalyticsPage (Admin only)
    ├── categories/
    │   └── page.tsx                    ← CategoryManagerPage (Admin)
    ├── tags/
    │   └── page.tsx                    ← TagManagerPage (Admin)
    ├── templates/
    │   └── page.tsx                    ← PostTemplatePage
    ├── layout-templates/
    │   └── page.tsx                    ← LayoutTemplatePage (Admin)
    └── [postId]/
        ├── layout.tsx                  ← PostDetailLayout với tab navigation
        ├── page.tsx                    ← Tab "Nội dung" — PostForm
        ├── media/
        │   └── page.tsx                ← Tab "Media" — MediaGallery
        ├── banners/
        │   └── page.tsx                ← Tab "Banner" — BannerLayoutGrid
        ├── ai/
        │   └── page.tsx                ← Tab "AI" — AIGenerationPanel
        └── versions/
            └── page.tsx                ← Tab "Versions" — VersionTimeline
```

---

## 14. Thứ Tự Implement (Recommended)

### Phase 1 — Core (Tuần 1)

1. `types.ts` + `constants.ts` — khai báo toàn bộ types và constants
2. `api.ts` — API layer hoàn chỉnh (chưa cần test, chỉ cần type-safe)
3. `PostTable` + `PostFilterBar` + `PostListPage` — danh sách bài, filter
4. `PostForm` + `CreatePostPage` — tạo/sửa bài (form đơn giản trước)
5. `PostDetailPage` với tab structure
6. `PostActionBar` — submit review / approve / reject
7. `MediaGallery` + `MediaUploadZone`

### Phase 2 — AI & Banner (Tuần 2)

8. `AIGenerationPanel` + polling hook
9. `AIVariantCards` + `HashtagSuggestions`
10. `BannerLayoutGrid` + `BannerLayoutCard`
11. `BannerLayoutEditor` + `BannerPreview` (JSON visual)
12. `GenerateBannerModal`

### Phase 3 — Taxonomy + Templates + Reviews (Tuần 3)

13. `CategoryTree` + `CategoryForm` + `CategoryManagerPage`
14. `TagGrid` + `TagAutocomplete` (multi-select trong PostForm)
15. `PostTemplateGrid` + `LayoutTemplateGrid`
16. `ReviewQueuePage` + `RejectPostModal`
17. `VersionTimeline` + `VersionDiffViewer`

### Phase 4 — Analytics + Polish (Tuần 4)

18. `AnalyticsSummaryCards` + chart components
19. `ContentAnalyticsPage`
20. Auto-save draft logic
21. Character counter
22. Empty states và error states đầy đủ
