# Kế Hoạch Django App — `agents`

> **Mục tiêu:** Xây dựng một Django app trung tâm để lưu trữ và quản lý API keys của các nhà cung cấp AI bên ngoài (OpenAI, Anthropic, Google Gemini, v.v.), cung cấp internal Python API để các app khác trong dự án có thể sử dụng lại mà không cần tự cấu hình kết nối.

---

## 1. Tính Năng

### 1.1 MVP (Cần thiết ngay)

| # | Tính năng | Mô tả |
|---|-----------|-------|
| 1 | Quản lý Provider | CRUD nhà cung cấp AI (OpenAI, Anthropic, Gemini , z.ai ...) qua Admin API |
| 2 | Quản lý API Key | Thêm/sửa/xóa API key cho từng provider, key được **mã hóa tại DB** |
| 3 | Quản lý Agent Config | Lưu cấu hình model (model name, temperature, max_tokens...) per provider |
| 4 | Priority Key Selection | Khi gọi `get_active_key()` → tự chọn key active có priority cao nhất |
| 5 | Internal Python API | `AgentKeyService.get_active_key("openai")` dùng trong các app khác |
| 6 | Masking khi read | API response luôn trả key dạng masked (`sk-...****`), không lộ plain text |
| 7 | Soft delete | Provider, Key, Config đều hỗ trợ soft delete |

### 1.2 Tính Năng Sau (Có thể thêm)

| # | Tính năng | Mô tả |
|---|-----------|-------|
| 8 | Key Rotation | Tự động chuyển sang key tiếp theo khi key hiện tại fail (rate limit, expired) |
| 9 | Usage Tracking | Đếm số lần key được dùng, ghi lại `last_used_at` |
| 10 | Key Expiry | Đặt `expires_at` cho key, cảnh báo khi sắp hết hạn |
| 11 | Health Check Key | Cronjob định kỳ ping thử key xem còn hoạt động không |
| 12 | Multi-env Key | Phân biệt key môi trường: dev/staging/production |

---

## 2. Kiến Trúc Hệ Thống

### 2.1 Models

#### `AgentProvider` — Nhà cung cấp AI

```
AgentProvider
├── id             UUID (PK)
├── name           CharField(100)       — "OpenAI", "Anthropic", "Google Gemini"
├── slug           SlugField(unique)    — "openai", "anthropic", "gemini"
├── description    TextField(blank)     — Mô tả tùy chọn
├── website_url    URLField(blank)      — https://platform.openai.com
├── is_active      BooleanField         — default=True
├── created_at     DateTimeField
├── updated_at     DateTimeField
└── is_deleted     BooleanField         — soft delete
```

**Kế thừa:** `BaseModel` từ `common/models.py`

---

#### `AgentAPIKey` — API Key được mã hóa

```
AgentAPIKey
├── id             UUID (PK)
├── provider       FK → AgentProvider (on_delete=CASCADE)
├── name           CharField(100)       — "Production Key 1", "Backup Key"
├── encrypted_key  TextField            — key mã hóa bằng Fernet
├── key_preview    CharField(20)        — "sk-proj-...****" (lưu sẵn để hiển thị)
├── is_active      BooleanField         — default=True
├── priority       PositiveIntegerField — 1 = ưu tiên cao nhất
├── last_used_at   DateTimeField(null)  — cập nhật mỗi lần key được gọi
├── expires_at     DateTimeField(null)  — tuỳ chọn
├── created_by     FK → User(null)      — Admin tạo key
├── created_at     DateTimeField
├── updated_at     DateTimeField
└── is_deleted     BooleanField
```

**Quan hệ:**
- `AgentProvider` ← `AgentAPIKey` (one-to-many: một provider có nhiều key)
- `User` ← `AgentAPIKey` (ghi nhận ai tạo key)

**Bảo mật:**
- Field `encrypted_key` **không bao giờ trả về API response** — chỉ dùng nội bộ
- Field `key_preview` lưu dạng masked được tạo khi tạo key (không thể tái tạo)
- Encryption dùng `cryptography.fernet.Fernet`, encryption key lấy từ `settings.AGENT_ENCRYPTION_KEY`

---

#### `AgentConfig` — Cấu hình model AI

```
AgentConfig
├── id             UUID (PK)
├── provider       FK → AgentProvider (on_delete=CASCADE)
├── name           CharField(100)       — "Default GPT-4o", "Fast Mode"
├── model_name     CharField(100)       — "gpt-4o", "claude-3-5-sonnet-latest"
├── config_json    JSONField            — {"temperature": 0.7, "max_tokens": 2048}
├── is_default     BooleanField         — chỉ 1 config được là default/provider
├── is_active      BooleanField
├── created_at     DateTimeField
├── updated_at     DateTimeField
└── is_deleted     BooleanField
```

**Ràng buộc:**
- Constraint `unique_together` hoặc signal để đảm bảo chỉ 1 config `is_default=True` per provider

---

### 2.2 Quan Hệ Model

```
User
 └── (created_by) AgentAPIKey

AgentProvider
 ├── AgentAPIKey  [1 → nhiều]
 └── AgentConfig  [1 → nhiều]
```

---

### 2.3 Services

**`AgentKeyService`** — Logic nghiệp vụ chính

| Method | Input | Output | Mô tả |
|--------|-------|--------|-------|
| `get_active_key(provider_slug)` | `str` | `str` (plain key) | Lấy key decrypt, ưu tiên cao nhất còn active |
| `get_default_config(provider_slug)` | `str` | `dict` | Lấy config mặc định của provider |
| `get_config_by_name(provider_slug, name)` | `str, str` | `dict` | Lấy config theo tên |
| `create_key(provider_id, name, raw_key, ...)` | — | `AgentAPIKey` | Mã hóa rồi lưu key mới |
| `update_key_status(key_id, is_active)` | — | `AgentAPIKey` | Bật/tắt key |
| `mark_key_used(key_id)` | `UUID` | `None` | Cập nhật `last_used_at` |
| `rotate_key(provider_slug)` | `str` | `str` (plain key) | Lấy key active tiếp theo theo priority |

**`AgentEncryptionService`** — Xử lý mã hóa (internal)

| Method | Mô tả |
|--------|-------|
| `encrypt(raw_key)` | Mã hóa plain text key → Fernet token |
| `decrypt(encrypted_key)` | Giải mã → plain text key |
| `generate_preview(raw_key)` | Tạo masked preview (e.g. `sk-proj-AbCd...****`) |

---

### 2.4 Selectors

**`AgentSelector`** — Query không có side effect

| Method | Mô tả |
|--------|-------|
| `get_provider_by_slug(slug)` | Lấy provider, raise `AgentProviderNotFound` nếu không có |
| `get_active_keys(provider_id)` | Queryset các key active, sắp xếp theo `priority` ASC |
| `get_default_config(provider_id)` | Config có `is_default=True`, raise nếu không có |
| `list_providers(include_inactive)` | List tất cả providers |
| `list_keys_for_provider(provider_id)` | List keys (không decrypt) |

---

### 2.5 Exceptions

```python
# apps/agents/exceptions.py
AgentProviderNotFound       # 404 — không tìm thấy provider
AgentAPIKeyNotFound         # 404 — không có key nào active
AgentConfigNotFound         # 404 — không tìm thấy config
AgentDecryptionError        # 500 — lỗi giải mã key
```

---

## 3. Internal Python API (Dùng Trong Các App Khác)

Đây là phần quan trọng nhất — cách các **app khác** trong project sử dụng `agents` app mà **không cần cấu hình lại**:

```python
# Trong bất kỳ app nào (ví dụ: apps/chat/, apps/summarizer/)
from apps.agents.services.agent_key_service import AgentKeyService

# --- Lấy API key ---
api_key = AgentKeyService.get_active_key("openai")
# → "sk-proj-AbCdEfGhIjKlMnOpQrStUvWx..."

# --- Lấy config mặc định ---
config = AgentKeyService.get_default_config("openai")
# → {"model_name": "gpt-4o", "temperature": 0.7, "max_tokens": 2048}

# --- Lấy config theo tên ---
config = AgentKeyService.get_config_by_name("anthropic", "Fast Mode")
# → {"model_name": "claude-3-5-haiku", "temperature": 0.5, "max_tokens": 1024}

# --- Sử dụng với OpenAI SDK ---
import openai
client = openai.OpenAI(api_key=AgentKeyService.get_active_key("openai"))
```

---

## 4. API Endpoints

> Permission: Tất cả endpoints chỉ dành cho **Admin** (`IsAdminUser`) trừ khi có ghi chú khác.
> Prefix: `/api/v1/agents/`

---

### 4.1 Providers

#### `GET /api/v1/agents/providers/`

| | |
|--|--|
| **Mục đích** | List tất cả providers |
| **Permission** | IsAdminUser |
| **Query params** | `?is_active=true` (optional filter) |

**Response 200:**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "OpenAI",
      "slug": "openai",
      "description": "OpenAI GPT models",
      "website_url": "https://platform.openai.com",
      "is_active": true,
      "keys_count": 3,
      "active_keys_count": 2
    }
  ],
  "message": "success"
}
```

---

#### `POST /api/v1/agents/providers/`

| | |
|--|--|
| **Mục đích** | Tạo provider mới |
| **Permission** | IsAdminUser |

**Input:**
```json
{
  "name": "OpenAI",
  "slug": "openai",
  "description": "OpenAI GPT models",
  "website_url": "https://platform.openai.com",
  "is_active": true
}
```

**Response 201:** Provider object đã tạo

---

#### `GET /api/v1/agents/providers/{slug}/`

| | |
|--|--|
| **Mục đích** | Xem chi tiết provider |
| **Permission** | IsAdminUser |

**Response 200:** Provider object + danh sách keys (masked) + configs

---

#### `PATCH /api/v1/agents/providers/{slug}/`

| | |
|--|--|
| **Mục đích** | Cập nhật thông tin provider |
| **Permission** | IsAdminUser |

---

#### `DELETE /api/v1/agents/providers/{slug}/`

| | |
|--|--|
| **Mục đích** | Soft delete provider (và cascade soft delete toàn bộ keys + configs) |
| **Permission** | IsAdminUser |

**Response 204**

---

### 4.2 API Keys

#### `GET /api/v1/agents/providers/{slug}/keys/`

| | |
|--|--|
| **Mục đích** | List keys của provider (masked — không trả plain text) |
| **Permission** | IsAdminUser |

**Response 200:**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Production Key 1",
      "key_preview": "sk-proj-AbCd...****",
      "is_active": true,
      "priority": 1,
      "last_used_at": "2026-04-09T10:00:00Z",
      "expires_at": null,
      "created_by": "admin@example.com",
      "created_at": "2026-01-01T00:00:00Z"
    }
  ],
  "message": "success"
}
```

---

#### `POST /api/v1/agents/providers/{slug}/keys/`

| | |
|--|--|
| **Mục đích** | Thêm key mới cho provider |
| **Permission** | IsAdminUser |

**Input:**
```json
{
  "name": "Production Key 1",
  "raw_key": "sk-proj-AbCdEfGhIjKl...",
  "priority": 1,
  "expires_at": null
}
```

**Logic:**
1. Nhận `raw_key` từ request
2. Gọi `AgentEncryptionService.encrypt(raw_key)` → lưu vào `encrypted_key`
3. Gọi `AgentEncryptionService.generate_preview(raw_key)` → lưu vào `key_preview`
4. **Không bao giờ lưu hoặc trả về `raw_key` sau bước này**

**Response 201:**
```json
{
  "data": {
    "id": "uuid",
    "name": "Production Key 1",
    "key_preview": "sk-proj-AbCd...****",
    "is_active": true,
    "priority": 1
  },
  "message": "API key đã được thêm thành công"
}
```

---

#### `PATCH /api/v1/agents/providers/{slug}/keys/{id}/`

| | |
|--|--|
| **Mục đích** | Cập nhật thông tin key (name, priority, is_active, expires_at) — **không cho sửa key value** |
| **Permission** | IsAdminUser |

**Input:**
```json
{
  "name": "Backup Key",
  "is_active": false,
  "priority": 2
}
```

---

#### `DELETE /api/v1/agents/providers/{slug}/keys/{id}/`

| | |
|--|--|
| **Mục đích** | Soft delete key |
| **Permission** | IsAdminUser |

**Response 204**

---

### 4.3 Configs

#### `GET /api/v1/agents/providers/{slug}/configs/`

| | |
|--|--|
| **Mục đích** | List configs của provider |
| **Permission** | IsAdminUser |

**Response 200:**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Default GPT-4o",
      "model_name": "gpt-4o",
      "config_json": {"temperature": 0.7, "max_tokens": 2048},
      "is_default": true,
      "is_active": true
    }
  ]
}
```

---

#### `POST /api/v1/agents/providers/{slug}/configs/`

| | |
|--|--|
| **Mục đích** | Tạo config mới |
| **Permission** | IsAdminUser |

**Input:**
```json
{
  "name": "Default GPT-4o",
  "model_name": "gpt-4o",
  "config_json": {
    "temperature": 0.7,
    "max_tokens": 2048,
    "top_p": 1.0
  },
  "is_default": true
}
```

**Logic:** Nếu `is_default=true` → tự động set `is_default=false` cho các config khác của cùng provider

---

#### `PATCH /api/v1/agents/providers/{slug}/configs/{id}/`

| | |
|--|--|
| **Mục đích** | Cập nhật config |
| **Permission** | IsAdminUser |

---

#### `DELETE /api/v1/agents/providers/{slug}/configs/{id}/`

| | |
|--|--|
| **Mục đích** | Soft delete config |
| **Permission** | IsAdminUser |

**Response 204**

---

## 5. Luồng Hoạt Động

### 5.1 Luồng Thêm Key Mới (Admin)

```
Admin → POST /api/v1/agents/providers/openai/keys/
        { "name": "Prod Key", "raw_key": "sk-...", "priority": 1 }
          ↓
AgentAPIKeySerializer.validate()
  → Kiểm tra provider tồn tại và active
          ↓
AgentKeyService.create_key()
  → AgentEncryptionService.encrypt(raw_key) → encrypted_key
  → AgentEncryptionService.generate_preview(raw_key) → "sk-...****"
  → Lưu DB (raw_key không được lưu)
          ↓
Response 201: { key_preview, id, name, is_active, priority }
```

---

### 5.2 Luồng App Khác Gọi Internal API

```
apps/chat/services/chat_service.py
  → AgentKeyService.get_active_key("openai")
      ↓
  AgentSelector.get_provider_by_slug("openai")
    → raise AgentProviderNotFound nếu không có / inactive
      ↓
  AgentSelector.get_active_keys(provider_id)
    → QuerySet: filter(is_active=True, is_deleted=False).order_by("priority")
    → raise AgentAPIKeyNotFound nếu queryset rỗng
      ↓
  Lấy key đầu tiên (priority cao nhất)
  AgentEncryptionService.decrypt(encrypted_key) → plain_key
  AgentKeyService.mark_key_used(key.id) [async/background]
      ↓
  return plain_key
```

---

### 5.3 Luồng Soft Delete Provider

```
Admin → DELETE /api/v1/agents/providers/openai/
          ↓
AgentKeyService.soft_delete_provider(slug)
  → provider.soft_delete()
  → AgentAPIKey.objects.filter(provider=provider).update(is_deleted=True)
  → AgentConfig.objects.filter(provider=provider).update(is_deleted=True)
          ↓
Response 204
```

---

## 6. Cấu Trúc Folder

```
apps/agents/
├── __init__.py
├── admin.py                     # Register models vào Django admin
├── apps.py                      # AppConfig — name = "apps.agents"
├── exceptions.py                # AgentProviderNotFound, AgentAPIKeyNotFound...
├── urls.py                      # URL routing cho agents
│
├── models/
│   ├── __init__.py              # Export: AgentProvider, AgentAPIKey, AgentConfig
│   ├── agent_provider.py        # Model AgentProvider
│   ├── agent_api_key.py         # Model AgentAPIKey
│   └── agent_config.py          # Model AgentConfig
│
├── serializers/
│   ├── __init__.py
│   ├── provider_serializer.py   # AgentProvider read/write serializers
│   ├── key_serializer.py        # AgentAPIKey — write nhận raw_key, read trả masked
│   └── config_serializer.py     # AgentConfig serializer
│
├── services/
│   ├── __init__.py
│   ├── agent_key_service.py     # AgentKeyService — business logic chính
│   └── agent_encryption_service.py  # Fernet encrypt/decrypt
│
├── selectors/
│   ├── __init__.py
│   └── agent_selector.py        # Database queries (read-only logic)
│
├── views/
│   ├── __init__.py
│   ├── provider_views.py        # CRUD views cho AgentProvider
│   ├── key_views.py             # CRUD views cho AgentAPIKey
│   └── config_views.py          # CRUD views cho AgentConfig
│
├── migrations/
│   └── __init__.py
│
└── tests/
    └── __init__.py
```

---

## 7. Yêu Cầu Kỹ Thuật

### 7.1 Python Dependencies

```
# requirements/base.txt — thêm vào
cryptography>=42.0.0   # Fernet encryption cho API keys
```

### 7.2 Django Settings

```python
# config/settings/base.py — thêm vào
INSTALLED_APPS += ["apps.agents"]

# .env — thêm biến môi trường
AGENT_ENCRYPTION_KEY=<base64-encoded-fernet-key-32-bytes>
```

> Tạo key bằng: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

### 7.3 Bảo Mật

| Quy tắc | Chi tiết |
|---------|----------|
| Không lưu plain text key | `encrypted_key` luôn là Fernet token |
| Không trả key trong response | API chỉ trả `key_preview` (masked) |
| Encryption key trong env | `AGENT_ENCRYPTION_KEY` không được hardcode |
| Permission | Tất cả endpoints yêu cầu `IsAdminUser` |
| Soft delete | Key không bao giờ bị xóa vật lý khỏi DB |

---

## 8. Ví Dụ Sử Dụng Trong App Mới

Khi tạo app mới (ví dụ: `apps/summarizer`), chỉ cần:

```python
# apps/summarizer/services/summarizer_service.py
from apps.agents.services.agent_key_service import AgentKeyService
from apps.agents.exceptions import AgentAPIKeyNotFound, AgentProviderNotFound

import anthropic

class SummarizerService:
    @staticmethod
    def summarize(text: str) -> str:
        try:
            api_key = AgentKeyService.get_active_key("anthropic")
            config = AgentKeyService.get_default_config("anthropic")
        except (AgentProviderNotFound, AgentAPIKeyNotFound) as e:
            raise SummarizerUnavailable("Dịch vụ AI chưa được cấu hình") from e

        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=config["model_name"],
            max_tokens=config.get("max_tokens", 1024),
            messages=[{"role": "user", "content": f"Tóm tắt: {text}"}]
        )
        return message.content[0].text
```

**Điều kiện tiên quyết duy nhất:** Admin đã thêm provider `anthropic` và ít nhất 1 active key + 1 default config qua Admin API — không cần thay đổi code.

---

## 9. Chiến Lược Mở Rộng

### 9.1 Nguyên Tắc Cốt Lõi — Provider là Đơn Vị Độc Lập

Toàn bộ kiến trúc xoay quanh `slug` của provider. Mỗi provider hoàn toàn **tách biệt về dữ liệu, keys, config và logic xử lý**. Thêm provider mới = thêm 1 bản ghi DB, không chạm vào code.

```
openai   → keys riêng → configs riêng → rate limit riêng → không ảnh hưởng anthropic
anthropic → keys riêng → configs riêng → rate limit riêng → không ảnh hưởng gemini
gemini   → keys riêng → configs riêng → rate limit riêng → không ảnh hưởng openai
```

---

### 9.2 Thêm Provider Mới — Zero Code Change

Khi cần thêm nhà cung cấp mới (vd: `xai`, `mistral`, `cohere`):

1. Admin gọi `POST /api/v1/agents/providers/` với `slug="mistral"`
2. Admin thêm key qua `POST /api/v1/agents/providers/mistral/keys/`
3. Admin thêm config qua `POST /api/v1/agents/providers/mistral/configs/`
4. App mới gọi `AgentKeyService.get_active_key("mistral")` — **không sửa file nào**

> Không cần migration mới, không cần sửa service, không cần restart — chỉ cần dữ liệu DB.

---

### 9.3 Cô Lập Hoàn Toàn Giữa Các Provider (Không Chồng Chéo)

#### 9.3.1 Cô Lập Keys — DB Level

Mỗi `AgentAPIKey` có FK trực tiếp tới `AgentProvider`. Query luôn filter theo `provider_id`:

```python
# Trong AgentSelector — không bao giờ có query cross-provider
AgentAPIKey.objects.filter(
    provider=provider,        # LUÔN có filter này
    is_active=True,
    is_deleted=False
).order_by("priority")
```

Không có global key pool — OpenAI key **không thể** bị nhầm sang Anthropic.

#### 9.3.2 Cô Lập Config — Constraint DB

`AgentConfig` cũng FK tới `AgentProvider`. Config `is_default=True` được enforce per-provider bởi signal/service:

```python
# Chỉ reset is_default trong scope của CÙNG provider
AgentConfig.objects.filter(
    provider=provider,         # Scoped theo provider
    is_default=True
).update(is_default=False)
```

Config của OpenAI không thể conflict với config của Gemini.

#### 9.3.3 Cô Lập Priority — Per-Provider

Field `priority` trên `AgentAPIKey` có nghĩa trong phạm vi **từng provider riêng biệt**:

```
openai   key priority 1 → key "Prod Key"
openai   key priority 2 → key "Backup Key"

anthropic key priority 1 → key "Claude Main"   ← priority 1 ở đây ≠ priority 1 của openai
```

Không có ranking toàn cục — mỗi priority list chạy độc lập.

---

### 9.4 Xử Lý Parallel Calls Không Gây Nghẽn

#### 9.4.1 Vấn Đề: `mark_key_used` Gây Contention

Nếu nhiều request đồng thời gọi cùng 1 key → nhiều thread cùng `UPDATE last_used_at` → row-level lock:

```
Request A: UPDATE agent_api_keys SET last_used_at=NOW() WHERE id='abc'  ← lock row
Request B: UPDATE agent_api_keys SET last_used_at=NOW() WHERE id='abc'  ← chờ lock
Request C: UPDATE agent_api_keys SET last_used_at=NOW() WHERE id='abc'  ← chờ lock
```

**Giải pháp:** `mark_key_used` dùng Celery task bất đồng bộ (fire-and-forget):

```python
# AgentKeyService.get_active_key()
plain_key = AgentEncryptionService.decrypt(key.encrypted_key)

# Không block request — ghi usage sau
from tasks.agent_tasks import task_mark_key_used
task_mark_key_used.delay(str(key.id))  # Celery async

return plain_key  # Return ngay, không chờ DB write
```

#### 9.4.2 `get_active_key` là Read-Only — Safe Cho Parallel

Bước quan trọng `get_active_key` chỉ thực hiện SELECT:

```python
# Không có lock, không có write — N requests đồng thời đều safe
AgentAPIKey.objects.filter(...).order_by("priority").first()
```

Không có transaction, không có lock → 1000 requests đồng thời vào cùng 1 provider không block nhau.

#### 9.4.3 Cache Provider Lookup (Tùy Chọn — Khi Scale)

Nếu traffic cao, `get_provider_by_slug` gọi DB mỗi request. Khi cần, thêm cache:

```python
# AgentSelector — thêm sau khi cần thiết
from django.core.cache import cache

@staticmethod
def get_provider_by_slug(slug: str) -> AgentProvider:
    cache_key = f"agent_provider:{slug}"
    provider = cache.get(cache_key)
    if provider is None:
        provider = AgentProvider.objects.get(slug=slug, is_active=True, is_deleted=False)
        cache.set(cache_key, provider, timeout=300)  # 5 phút
    return provider
```

Cache invalidate khi admin update provider → thêm signal `post_save` xóa cache.

---

### 9.5 Mở Rộng Logic Per-Provider (Không Ảnh Hưởng Provider Khác)

Khi một provider cần xử lý đặc biệt (vd: OpenAI dùng Organization ID, Azure dùng endpoint khác):

**Cách 1 — Dùng `config_json` (Không cần code mới):**

```json
// AgentConfig.config_json cho Azure OpenAI
{
  "model_name": "gpt-4o",
  "temperature": 0.7,
  "azure_endpoint": "https://my-resource.openai.azure.com",
  "api_version": "2024-02-01"
}
```

App tiêu thụ tự đọc extra fields từ config dict — `agents` app không cần biết.

**Cách 2 — Thêm method vào `AgentKeyService` (Isolated Extension):**

```python
# Thêm method mới không ảnh hưởng method hiện có
@staticmethod
def get_azure_client_config(provider_slug: str) -> dict:
    """Chỉ dành cho Azure OpenAI — các provider khác không gọi method này."""
    config = AgentKeyService.get_default_config(provider_slug)
    return {
        "api_key": AgentKeyService.get_active_key(provider_slug),
        "azure_endpoint": config.get("azure_endpoint"),
        "api_version": config.get("api_version"),
    }
```

Method mới **không chạm** vào logic của các provider khác.

---

### 9.6 Lộ Trình Mở Rộng Theo Giai Đoạn

| Giai đoạn | Khi nào cần | Việc cần làm | Code thay đổi |
|-----------|-------------|--------------|---------------|
| **MVP** | Ngay bây giờ | Implement theo plan này | — |
| **Key Rotation** | Khi 1 key bị rate-limit | Thêm `rotate_key()` trong service + retry logic | Chỉ `agent_key_service.py` |
| **Usage Tracking** | Muốn báo cáo usage | Thêm model `AgentKeyUsageLog` riêng | Thêm model mới, không sửa model cũ |
| **Key Expiry Alert** | Quản lý key có thời hạn | Thêm Celery beat task kiểm tra `expires_at` | Chỉ `tasks/agent_tasks.py` |
| **Cache Layer** | Traffic > 100 req/s | Thêm Redis cache vào `AgentSelector` | Chỉ `agent_selector.py` |
| **Multi-env Key** | Cần key riêng dev/prod | Thêm field `environment` vào `AgentAPIKey` | 1 migration + 1 field |
| **Health Check Key** | Key hay bị hỏng | Thêm Celery beat task ping định kỳ | Thêm task mới |

> Mỗi giai đoạn tiếp theo **chỉ thêm, không sửa** — Open/Closed Principle theo nghĩa thực tế.
