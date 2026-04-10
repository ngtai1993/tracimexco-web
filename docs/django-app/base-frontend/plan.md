# Kế Hoạch Django App — `appearance`

> **Mục tiêu:** Xây dựng một Django app trung tâm để quản lý **design tokens** (màu sắc, typography) và **media assets** (logo, ảnh, favicon...) của website. Backend admin có thể tùy chỉnh qua Admin API; frontend tiêu thụ qua một endpoint duy nhất để render đúng thương hiệu mà không cần deploy lại.

---

## 1. Tính Năng

### 1.1 MVP (Cần thiết ngay)

| # | Tính năng | Mô tả |
|---|-----------|-------|
| 1 | Quản lý Color Token | CRUD color token theo nhóm (brand, semantic, neutral) — mỗi token là 1 cặp key/hex |
| 2 | Quản lý Media Asset | Upload và đặt tên cho ảnh (logo, favicon, og_image, banner...) |
| 3 | Endpoint Public Config | `GET /api/v1/appearance/config/` → trả toàn bộ tokens + assets cho frontend |
| 4 | Cache Response | Response được cache (Redis/memory), tự invalidate khi admin cập nhật |
| 5 | Soft Delete | Tất cả model hỗ trợ soft delete |
| 6 | Admin Interface | Quản lý qua Django Admin với preview màu sắc và ảnh |

### 1.2 Tính Năng Sau (Có thể thêm)

| # | Tính năng | Mô tả |
|---|-----------|-------|
| 7 | Multi-theme | Hỗ trợ nhiều theme (light/dark/brand variant), frontend chọn theme theo context |
| 8 | CSS Variables Export | Endpoint trả về file `.css` chứa CSS custom properties |
| 9 | Revision History | Lịch sử thay đổi token/asset, có thể rollback |
| 10 | Typography Token | Quản lý thêm font-family, font-size scale, line-height |

---

## 2. Kiến Trúc Hệ Thống

### 2.1 Models

#### `ColorToken` — Design token màu sắc

```
ColorToken
├── id           UUID (PK)
├── name         CharField(100)        — "Primary", "Secondary", "Danger"
├── key          SlugField(unique)     — "primary", "secondary", "danger" (dùng làm CSS var name)
├── value        CharField(20)         — "#1A56DB" (hex color)
├── group        CharField(50)         — "brand" | "semantic" | "neutral" | "custom"
├── description  TextField(blank)      — Mô tả cách dùng token
├── order        PositiveIntegerField  — Thứ tự hiển thị trong UI
├── is_active    BooleanField          — default=True
├── created_at   DateTimeField
├── updated_at   DateTimeField
└── is_deleted   BooleanField
```

**Kế thừa:** `BaseModel` từ `common/models.py`

**Quy ước `group`:**

| Group | Ý nghĩa | Ví dụ key |
|-------|---------|-----------|
| `brand` | Màu chủ đạo thương hiệu | `primary`, `secondary`, `accent` |
| `semantic` | Màu theo ngữ nghĩa | `success`, `warning`, `danger`, `info` |
| `neutral` | Màu trung tính | `fg`, `fg-muted`, `bg`, `bg-subtle`, `border` |
| `custom` | Màu đặc thù dự án | Tùy ý |

---

#### `MediaAsset` — Ảnh và file media được đặt tên

```
MediaAsset
├── id           UUID (PK)
├── name         CharField(100)        — "Logo chính", "Logo nền tối", "Hero Banner"
├── key          SlugField(unique)     — "logo", "logo-dark", "hero-banner", "favicon", "og-image"
├── file         ImageField            — upload_to="appearance/media/%Y/%m/"
├── alt_text     CharField(200, blank) — Alt text cho SEO / accessibility
├── description  TextField(blank)      — Ghi chú nội bộ cho admin
├── is_active    BooleanField          — default=True
├── created_at   DateTimeField
├── updated_at   DateTimeField
└── is_deleted   BooleanField
```

**Key chuẩn được định nghĩa sẵn:**

| Key | Mô tả |
|-----|-------|
| `logo` | Logo chính (dùng trên nền sáng) |
| `logo-dark` | Logo dùng trên nền tối |
| `favicon` | Icon tab trình duyệt (32×32 hoặc SVG) |
| `og-image` | Ảnh khi share lên mạng xã hội (1200×630) |
| `hero-banner` | Ảnh banner trang chủ |

Frontend dùng `key` làm định danh — không hardcode URL.

---

### 2.2 Quan Hệ Model

```
ColorToken  (độc lập)
MediaAsset  (độc lập)
```

Hai model không có quan hệ trực tiếp với nhau. Chúng được gom lại tại **selector layer** và trả về qua một endpoint duy nhất.

---

### 2.3 Services

#### `AppearanceCacheService`

| Method | Mô tả |
|--------|-------|
| `get_config()` | Đọc cache; nếu miss thì build từ DB và set cache |
| `invalidate_config()` | Xóa cache (gọi sau mỗi lần save/delete token hoặc asset) |

**Cache key:** `"appearance:config"` — TTL: 3600s (1 giờ hoặc cho đến khi bị invalidate).

Cache invalidation xảy ra qua **Django signal** `post_save` và `post_delete` trên `ColorToken` và `MediaAsset`.

---

### 2.4 Selectors

#### `AppearanceSelector`

| Method | Mô tả |
|--------|-------|
| `get_active_color_tokens(mode)` | Trả các `ColorToken` active theo `mode` (`"light"` hoặc `"dark"`), sắp xếp theo `group` rồi `order` |
| `get_active_media_assets()` | Trả các `MediaAsset` active |
| `build_config_payload()` | Gom token light + dark + asset thành dict response |

---

## 3. Đặc Tả API Endpoints

> Base URL: `/api/v1/appearance/`
> Response format theo chuẩn project: `{ "data": ..., "message": ... }`

---

### `GET /api/v1/appearance/config/`

| | |
|--|--|
| **Mục đích** | Trả toàn bộ design tokens và media assets để frontend khởi tạo theme |
| **Permission** | `AllowAny` — public endpoint, không cần auth |
| **Cache** | Response được cache 1 giờ, invalidate ngay khi có thay đổi |
| **Throttle** | `AnonRateThrottle` (100/min) |

**Response 200:**
```json
{
  "data": {
    "colors": {
      "light": {
        "brand": [
          { "key": "primary",      "value": "#0e4475", "name": "Primary" },
          { "key": "primary-hover","value": "#0b3560", "name": "Primary Hover" },
          { "key": "primary-light","value": "#e6eef7", "name": "Primary Light" },
          { "key": "primary-fg",   "value": "#ffffff", "name": "Primary Foreground" },
          { "key": "secondary",    "value": "#1565c0", "name": "Secondary" },
          { "key": "accent",       "value": "#0288d1", "name": "Accent" }
        ],
        "semantic": [
          { "key": "success",       "value": "#16a34a", "name": "Success" },
          { "key": "success-light", "value": "#dcfce7", "name": "Success Light" },
          { "key": "warning",       "value": "#d97706", "name": "Warning" },
          { "key": "warning-light", "value": "#fef3c7", "name": "Warning Light" },
          { "key": "danger",        "value": "#dc2626", "name": "Danger" },
          { "key": "danger-light",  "value": "#fee2e2", "name": "Danger Light" },
          { "key": "info",          "value": "#0284c7", "name": "Info" },
          { "key": "info-light",    "value": "#e0f2fe", "name": "Info Light" }
        ],
        "neutral": [
          { "key": "fg",         "value": "#0f172a", "name": "Foreground" },
          { "key": "fg-muted",   "value": "#475569", "name": "Foreground Muted" },
          { "key": "fg-subtle",  "value": "#94a3b8", "name": "Foreground Subtle" },
          { "key": "bg",         "value": "#ffffff", "name": "Background" },
          { "key": "bg-subtle",  "value": "#f8fafc", "name": "Background Subtle" },
          { "key": "bg-muted",   "value": "#f1f5f9", "name": "Background Muted" },
          { "key": "border",     "value": "#e2e8f0", "name": "Border" },
          { "key": "card",       "value": "#ffffff", "name": "Card" },
          { "key": "card-border","value": "#e2e8f0", "name": "Card Border" }
        ]
      },
      "dark": {
        "brand": [
          { "key": "primary",      "value": "#2b78cc", "name": "Primary" },
          { "key": "primary-hover","value": "#3d8fdb", "name": "Primary Hover" },
          { "key": "primary-light","value": "#0d253d", "name": "Primary Light" },
          { "key": "primary-fg",   "value": "#ffffff", "name": "Primary Foreground" },
          { "key": "secondary",    "value": "#42a5f5", "name": "Secondary" },
          { "key": "accent",       "value": "#29b6f6", "name": "Accent" }
        ],
        "semantic": [
          { "key": "success",       "value": "#4ade80", "name": "Success" },
          { "key": "success-light", "value": "#052e16", "name": "Success Light" },
          { "key": "warning",       "value": "#fbbf24", "name": "Warning" },
          { "key": "warning-light", "value": "#2d1a00", "name": "Warning Light" },
          { "key": "danger",        "value": "#f87171", "name": "Danger" },
          { "key": "danger-light",  "value": "#2d0a0a", "name": "Danger Light" },
          { "key": "info",          "value": "#38bdf8", "name": "Info" },
          { "key": "info-light",    "value": "#021d2e", "name": "Info Light" }
        ],
        "neutral": [
          { "key": "fg",         "value": "#f1f5f9", "name": "Foreground" },
          { "key": "fg-muted",   "value": "#94a3b8", "name": "Foreground Muted" },
          { "key": "fg-subtle",  "value": "#64748b", "name": "Foreground Subtle" },
          { "key": "bg",         "value": "#0c1a2e", "name": "Background" },
          { "key": "bg-subtle",  "value": "#112036", "name": "Background Subtle" },
          { "key": "bg-muted",   "value": "#162843", "name": "Background Muted" },
          { "key": "border",     "value": "#1e3a5f", "name": "Border" },
          { "key": "card",       "value": "#112036", "name": "Card" },
          { "key": "card-border","value": "#1e3a5f", "name": "Card Border" }
        ]
      }
    },
    "media": {
      "logo":       { "url": "https://cdn.example.com/appearance/media/logo.svg",       "alt": "Logo công ty" },
      "logo-dark":  { "url": "https://cdn.example.com/appearance/media/logo-dark.svg", "alt": "Logo nền tối" },
      "favicon":    { "url": "https://cdn.example.com/appearance/media/favicon.png",   "alt": "" },
      "og-image":   { "url": "https://cdn.example.com/appearance/media/og.jpg",        "alt": "Open Graph" },
      "hero-banner":{ "url": "https://cdn.example.com/appearance/media/hero.jpg",      "alt": "Trang chủ" }
    }
  },
  "message": "OK"
}
```

**Lưu ý:**
- `colors` chia thành 2 object `light` / `dark`, mỗi object nhóm theo `group`.
- Frontend dùng `light` cho `:root`, `dark` cho `[data-theme="dark"]`.
- `media` dùng `key` làm object key → truy cập `config.media.logo.url` không cần vòng lặp.
- Token không active → không xuất hiện trong response.

---

### `GET /api/v1/appearance/config/css/`

| | |
|--|--|
| **Mục đích** | Trả CSS string chứa custom properties — dùng để inject vào `<style>` tag |
| **Permission** | `AllowAny` |
| **Content-Type** | `text/css` |
| **Cache** | Cùng cache key với endpoint trên |

**Response 200** (Content-Type: `text/css`):
```css
/* Light mode — default */
:root {
  --color-primary:       #0e4475;
  --color-primary-hover: #0b3560;
  --color-primary-light: #e6eef7;
  --color-primary-fg:    #ffffff;
  --color-secondary:     #1565c0;
  --color-accent:        #0288d1;

  --color-success:       #16a34a;
  --color-success-light: #dcfce7;
  --color-warning:       #d97706;
  --color-warning-light: #fef3c7;
  --color-danger:        #dc2626;
  --color-danger-light:  #fee2e2;
  --color-info:          #0284c7;
  --color-info-light:    #e0f2fe;

  --color-fg:            #0f172a;
  --color-fg-muted:      #475569;
  --color-fg-subtle:     #94a3b8;
  --color-bg:            #ffffff;
  --color-bg-subtle:     #f8fafc;
  --color-bg-muted:      #f1f5f9;
  --color-border:        #e2e8f0;
  --color-card:          #ffffff;
  --color-card-border:   #e2e8f0;
}

/* Dark mode */
[data-theme="dark"] {
  --color-primary:       #2b78cc;
  --color-primary-hover: #3d8fdb;
  --color-primary-light: #0d253d;
  --color-primary-fg:    #ffffff;
  --color-secondary:     #42a5f5;
  --color-accent:        #29b6f6;

  --color-success:       #4ade80;
  --color-success-light: #052e16;
  --color-warning:       #fbbf24;
  --color-warning-light: #2d1a00;
  --color-danger:        #f87171;
  --color-danger-light:  #2d0a0a;
  --color-info:          #38bdf8;
  --color-info-light:    #021d2e;

  --color-fg:            #f1f5f9;
  --color-fg-muted:      #94a3b8;
  --color-fg-subtle:     #64748b;
  --color-bg:            #0c1a2e;
  --color-bg-subtle:     #112036;
  --color-bg-muted:      #162843;
  --color-border:        #1e3a5f;
  --color-card:          #112036;
  --color-card-border:   #1e3a5f;
}
```

**Quy ước đặt tên CSS variable:** `--color-{key}` — frontend có thể dùng trực tiếp trong Tailwind CSS (`var(--color-primary)`).

Frontend toggle dark mode chỉ cần set `data-theme="dark"` trên thẻ `<html>` — không cần gọi lại API.

---

### Admin APIs (IsAdminUser)

> Chỉ dùng qua Django Admin hoặc internal tooling. Không dùng cho frontend public.

#### Color Token

| Method | URL | Mô tả |
|--------|-----|-------|
| `GET`    | `/api/v1/appearance/tokens/`         | Danh sách tất cả token (kể cả inactive) |
| `POST`   | `/api/v1/appearance/tokens/`         | Tạo token mới |
| `GET`    | `/api/v1/appearance/tokens/{id}/`    | Chi tiết token |
| `PATCH`  | `/api/v1/appearance/tokens/{id}/`    | Cập nhật token |
| `DELETE` | `/api/v1/appearance/tokens/{id}/`    | Soft delete token |

**Input tạo/cập nhật token:**
```json
{
  "name": "Primary",
  "key": "primary",
  "mode": "light",
  "value": "#0e4475",
  "group": "brand",
  "description": "Màu chủ đạo thương hiệu, dùng cho button và link chính",
  "order": 1,
  "is_active": true
}
```

**Validation:**
- `key`: chỉ slugs (`[a-z0-9-]`)
- `mode`: phải là `light` hoặc `dark`
- `key + mode`: unique (constraint DB)
- `value`: phải là hex hợp lệ (`#RRGGBB` hoặc `#RGB`)
- `group`: phải là một trong `brand | semantic | neutral | custom`

#### Media Asset

| Method | URL | Mô tả |
|--------|-----|-------|
| `GET`    | `/api/v1/appearance/assets/`         | Danh sách tất cả asset |
| `POST`   | `/api/v1/appearance/assets/`         | Upload asset mới (`multipart/form-data`) |
| `GET`    | `/api/v1/appearance/assets/{id}/`    | Chi tiết asset |
| `PATCH`  | `/api/v1/appearance/assets/{id}/`    | Cập nhật metadata hoặc thay file |
| `DELETE` | `/api/v1/appearance/assets/{id}/`    | Soft delete asset |

**Input upload asset** (`multipart/form-data`):
```
name        = "Logo chính"
key         = "logo"
file        = <ảnh binary>
alt_text    = "Logo công ty Tracimexco"
description = "SVG vector, nền trong suốt"
is_active   = true
```

**Validation:**
- `key`: unique, slugs
- `file`: chấp nhận `image/*`; giới hạn 5MB
- Nếu `key` đã tồn tại và `is_active=True`: file cũ bị thay thế (không xóa file cũ khỏi storage, chỉ update record)

---

## 4. Cấu Trúc File App

```
apps/appearance/
├── __init__.py
├── apps.py
├── admin.py                          # Django Admin với color preview
├── exceptions.py
├── urls.py
├── migrations/
│   └── __init__.py
├── models/
│   ├── __init__.py
│   ├── color_token.py                # ColorToken model
│   └── media_asset.py                # MediaAsset model
├── selectors/
│   ├── __init__.py
│   └── appearance_selector.py        # get_active_color_tokens(), build_config_payload()
├── serializers/
│   ├── __init__.py
│   ├── color_token_serializer.py
│   ├── media_asset_serializer.py
│   └── config_serializer.py          # AppearanceConfigSerializer (output endpoint public)
├── services/
│   ├── __init__.py
│   └── appearance_cache_service.py   # get_config(), invalidate_config()
├── signals.py                        # post_save / post_delete → invalidate cache
├── views/
│   ├── __init__.py
│   ├── config_views.py               # GET /config/ và GET /config/css/
│   ├── token_views.py                # CRUD ColorToken (admin)
│   └── asset_views.py                # CRUD MediaAsset (admin)
└── tests/
    ├── __init__.py
    ├── factories.py
    ├── test_models.py
    ├── test_selectors.py
    ├── test_services.py
    └── test_views.py
```

---

## 5. Luồng Hoạt Động

### 5.1 Frontend Load Theme (Happy Path)

```
Frontend boot
    │
    ▼
GET /api/v1/appearance/config/
    │
    ▼
AppearanceCacheService.get_config()
    │
    ├── Cache HIT? ──► Trả data từ Redis ngay
    │
    └── Cache MISS?
            │
            ▼
        AppearanceSelector.build_config_payload()
            │
            ├── get_active_color_tokens()  → QuerySet: ColorToken (is_active, not deleted)
            └── get_active_media_assets()  → QuerySet: MediaAsset (is_active, not deleted)
            │
            ▼
        Set cache (TTL 1h)
            │
            ▼
        Trả response JSON
```

### 5.2 Admin Cập Nhật Token

```
Admin PATCH /api/v1/appearance/tokens/{id}/
    │
    ▼
TokenView.partial_update()
    │
    ▼
ColorTokenSerializer.update() → save to DB
    │
    ▼
Signal: post_save → AppearanceCacheService.invalidate_config()
    │
    ▼
Cache bị xóa → Request tiếp theo sẽ rebuild từ DB
```

---

## 6. Data Seed Mặc Định

Tạo management command `seed_appearance` hoặc migration `RunPython` để tạo sẵn bộ token và asset placeholder khi setup dự án mới.

**Color Tokens mặc định:**

```python
# Mỗi token phải có 2 bản ghi: mode="light" và mode="dark"
DEFAULT_COLOR_TOKENS = [
    # ── BRAND ──────────────────────────────────────────────────────
    # Light
    {"key": "primary",       "mode": "light", "value": "#0e4475", "name": "Primary",            "group": "brand",    "order": 1},
    {"key": "primary-hover", "mode": "light", "value": "#0b3560", "name": "Primary Hover",       "group": "brand",    "order": 2},
    {"key": "primary-light", "mode": "light", "value": "#e6eef7", "name": "Primary Light",       "group": "brand",    "order": 3},
    {"key": "primary-fg",    "mode": "light", "value": "#ffffff", "name": "Primary Foreground",  "group": "brand",    "order": 4},
    {"key": "secondary",     "mode": "light", "value": "#1565c0", "name": "Secondary",           "group": "brand",    "order": 5},
    {"key": "accent",        "mode": "light", "value": "#0288d1", "name": "Accent",              "group": "brand",    "order": 6},
    # Dark
    {"key": "primary",       "mode": "dark",  "value": "#2b78cc", "name": "Primary",            "group": "brand",    "order": 1},
    {"key": "primary-hover", "mode": "dark",  "value": "#3d8fdb", "name": "Primary Hover",       "group": "brand",    "order": 2},
    {"key": "primary-light", "mode": "dark",  "value": "#0d253d", "name": "Primary Light",       "group": "brand",    "order": 3},
    {"key": "primary-fg",    "mode": "dark",  "value": "#ffffff", "name": "Primary Foreground",  "group": "brand",    "order": 4},
    {"key": "secondary",     "mode": "dark",  "value": "#42a5f5", "name": "Secondary",           "group": "brand",    "order": 5},
    {"key": "accent",        "mode": "dark",  "value": "#29b6f6", "name": "Accent",              "group": "brand",    "order": 6},

    # ── SEMANTIC ───────────────────────────────────────────────────
    # Light
    {"key": "success",       "mode": "light", "value": "#16a34a", "name": "Success",       "group": "semantic", "order": 1},
    {"key": "success-light", "mode": "light", "value": "#dcfce7", "name": "Success Light", "group": "semantic", "order": 2},
    {"key": "warning",       "mode": "light", "value": "#d97706", "name": "Warning",       "group": "semantic", "order": 3},
    {"key": "warning-light", "mode": "light", "value": "#fef3c7", "name": "Warning Light", "group": "semantic", "order": 4},
    {"key": "danger",        "mode": "light", "value": "#dc2626", "name": "Danger",        "group": "semantic", "order": 5},
    {"key": "danger-light",  "mode": "light", "value": "#fee2e2", "name": "Danger Light",  "group": "semantic", "order": 6},
    {"key": "info",          "mode": "light", "value": "#0284c7", "name": "Info",          "group": "semantic", "order": 7},
    {"key": "info-light",    "mode": "light", "value": "#e0f2fe", "name": "Info Light",    "group": "semantic", "order": 8},
    # Dark
    {"key": "success",       "mode": "dark",  "value": "#4ade80", "name": "Success",       "group": "semantic", "order": 1},
    {"key": "success-light", "mode": "dark",  "value": "#052e16", "name": "Success Light", "group": "semantic", "order": 2},
    {"key": "warning",       "mode": "dark",  "value": "#fbbf24", "name": "Warning",       "group": "semantic", "order": 3},
    {"key": "warning-light", "mode": "dark",  "value": "#2d1a00", "name": "Warning Light", "group": "semantic", "order": 4},
    {"key": "danger",        "mode": "dark",  "value": "#f87171", "name": "Danger",        "group": "semantic", "order": 5},
    {"key": "danger-light",  "mode": "dark",  "value": "#2d0a0a", "name": "Danger Light",  "group": "semantic", "order": 6},
    {"key": "info",          "mode": "dark",  "value": "#38bdf8", "name": "Info",          "group": "semantic", "order": 7},
    {"key": "info-light",    "mode": "dark",  "value": "#021d2e", "name": "Info Light",    "group": "semantic", "order": 8},

    # ── NEUTRAL ────────────────────────────────────────────────────
    # Light
    {"key": "fg",          "mode": "light", "value": "#0f172a", "name": "Foreground",        "group": "neutral", "order": 1},
    {"key": "fg-muted",    "mode": "light", "value": "#475569", "name": "Foreground Muted",  "group": "neutral", "order": 2},
    {"key": "fg-subtle",   "mode": "light", "value": "#94a3b8", "name": "Foreground Subtle", "group": "neutral", "order": 3},
    {"key": "bg",          "mode": "light", "value": "#ffffff", "name": "Background",        "group": "neutral", "order": 4},
    {"key": "bg-subtle",   "mode": "light", "value": "#f8fafc", "name": "Background Subtle", "group": "neutral", "order": 5},
    {"key": "bg-muted",    "mode": "light", "value": "#f1f5f9", "name": "Background Muted",  "group": "neutral", "order": 6},
    {"key": "border",      "mode": "light", "value": "#e2e8f0", "name": "Border",            "group": "neutral", "order": 7},
    {"key": "card",        "mode": "light", "value": "#ffffff", "name": "Card Background",   "group": "neutral", "order": 8},
    {"key": "card-border", "mode": "light", "value": "#e2e8f0", "name": "Card Border",       "group": "neutral", "order": 9},
    # Dark
    {"key": "fg",          "mode": "dark",  "value": "#f1f5f9", "name": "Foreground",        "group": "neutral", "order": 1},
    {"key": "fg-muted",    "mode": "dark",  "value": "#94a3b8", "name": "Foreground Muted",  "group": "neutral", "order": 2},
    {"key": "fg-subtle",   "mode": "dark",  "value": "#64748b", "name": "Foreground Subtle", "group": "neutral", "order": 3},
    {"key": "bg",          "mode": "dark",  "value": "#0c1a2e", "name": "Background",        "group": "neutral", "order": 4},
    {"key": "bg-subtle",   "mode": "dark",  "value": "#112036", "name": "Background Subtle", "group": "neutral", "order": 5},
    {"key": "bg-muted",    "mode": "dark",  "value": "#162843", "name": "Background Muted",  "group": "neutral", "order": 6},
    {"key": "border",      "mode": "dark",  "value": "#1e3a5f", "name": "Border",            "group": "neutral", "order": 7},
    {"key": "card",        "mode": "dark",  "value": "#112036", "name": "Card Background",   "group": "neutral", "order": 8},
    {"key": "card-border", "mode": "dark",  "value": "#1e3a5f", "name": "Card Border",       "group": "neutral", "order": 9},
]
```

**Bảng tham khảo màu sắc:**

| Token | Light | Dark | Ghi chú |
|-------|-------|------|--------|
| `primary` | `#0e4475` Dark Azure | `#2b78cc` | Màu chủ đạo thương hiệu |
| `primary-hover` | `#0b3560` | `#3d8fdb` | Trạng thái hover |
| `primary-light` | `#e6eef7` | `#0d253d` | Nền tint nhẹ (badge, highlight) |
| `secondary` | `#1565c0` | `#42a5f5` | Màu phụ |
| `accent` | `#0288d1` | `#29b6f6` | Nhấn mạnh |
| `success` | `#16a34a` | `#4ade80` | Thành công |
| `warning` | `#d97706` | `#fbbf24` | Cảnh báo |
| `danger` | `#dc2626` | `#f87171` | Lỗi / nguy hiểm |
| `info` | `#0284c7` | `#38bdf8` | Thông tin |
| `bg` | `#ffffff` | `#0c1a2e` Dark Navy | Nền chính |
| `border` | `#e2e8f0` | `#1e3a5f` | Đường viền |

**Media Asset placeholders:**

```python
DEFAULT_MEDIA_KEYS = [
    {"key": "logo",        "name": "Logo chính",     "alt_text": "Logo"},
    {"key": "logo-dark",   "name": "Logo nền tối",   "alt_text": "Logo"},
    {"key": "favicon",     "name": "Favicon",         "alt_text": ""},
    {"key": "og-image",    "name": "OG Image",        "alt_text": ""},
    {"key": "hero-banner", "name": "Hero Banner",     "alt_text": ""},
]
```

---

## 7. Cách Frontend Dùng

### 7.1 Inject CSS Variables (Next.js / React)

```tsx
// app/layout.tsx (Next.js App Router)
export default async function RootLayout({ children }) {
  const config = await fetch('/api/v1/appearance/config/').then(r => r.json())
  const { colors } = config.data

  // Build CSS variables cho từng mode
  const buildVars = (modeTokens: Record<string, { key: string; value: string }[]>) =>
    Object.values(modeTokens)
      .flat()
      .map(token => `  --color-${token.key}: ${token.value};`)
      .join('\n')

  const cssBlock = [
    `:root {\n${buildVars(colors.light)}\n}`,
    `[data-theme="dark"] {\n${buildVars(colors.dark)}\n}`,
  ].join('\n\n')

  return (
    <html suppressHydrationWarning>
      <head>
        <style dangerouslySetInnerHTML={{ __html: cssBlock }} />
      </head>
      <body>{children}</body>
    </html>
  )
}
```

**Toggle dark mode:**
```ts
// Chỉ cần set attribute trên <html> — CSS variables tự thay đổi
document.documentElement.setAttribute('data-theme', 'dark')
document.documentElement.setAttribute('data-theme', 'light')
```

Hoặc dùng endpoint CSS để inject qua `<link>` tag:
```html
<link rel="stylesheet" href="/api/v1/appearance/config/css/" />
```

### 7.2 Truy Cập Media Asset

```tsx
// frontend/src/lib/appearance.ts
export function getLogo(config: AppearanceConfig) {
  return config.data.media['logo']?.url ?? '/fallback-logo.svg'
}

// Dùng trong component
<img src={getLogo(config)} alt={config.data.media['logo']?.alt} />
```

### 7.3 Tailwind CSS Integration

```js
// tailwind.config.ts — dùng CSS variables thay vì hardcode
theme: {
  extend: {
    colors: {
      primary:   'var(--color-primary)',
      secondary: 'var(--color-secondary)',
      success:   'var(--color-success)',
      danger:    'var(--color-danger)',
      fg:        'var(--color-fg)',
      border:    'var(--color-border)',
    }
  }
}
```

Sau khi tích hợp: `className="bg-primary text-white"` sẽ dùng màu do backend quyết định — frontend không cần deploy lại khi admin đổi màu.

---

## 8. Dependency & Settings

```python
# requirements/base.txt (không cần thêm gì mới nếu dự án đã có Redis)
# Pillow     — đã có để dùng ImageField
# django-storages + boto3 — (optional) nếu lưu ảnh trên S3/CDN

# settings/base.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL"),
    }
}

APPEARANCE_CACHE_TTL = 3600          # 1 giờ
APPEARANCE_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```
