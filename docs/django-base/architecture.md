# Kiến Trúc & Cấu Trúc Dự Án

---

## 1. Cấu Trúc Thư Mục `backend/`

```
backend/
│
├── config/                          # Cấu hình project (không phải app)
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                  # Settings dùng chung
│   │   ├── development.py           # Override cho local dev
│   │   ├── staging.py
│   │   └── production.py
│   ├── urls.py                      # Root URL config
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                            # Chứa tất cả Django apps
│   ├── users/                       # User profile, quản lý tài khoản
│   │   ├── models/
│   │   ├── views/
│   │   ├── services/
│   │   ├── selectors/
│   │   ├── serializers/
│   │   ├── tests/
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── urls.py
│   │   ├── signals.py
│   │   ├── exceptions.py
│   │   └── constants.py
│   │
│   ├── authentication/              # JWT auth, đăng nhập, reset password
│   │   ├── views/
│   │   ├── services/
│   │   ├── serializers/
│   │   ├── tests/
│   │   ├── apps.py
│   │   └── urls.py
│   │
│   └── core/                        # App chia sẻ: health check, base views
│       ├── views/
│       ├── apps.py
│       └── urls.py
│
├── common/                          # Utilities dùng chung — KHÔNG phải app
│   ├── __init__.py
│   ├── models.py                    # BaseModel (timestamps, soft delete)
│   ├── serializers.py               # BaseSerializer
│   ├── pagination.py                # CustomPageNumberPagination
│   ├── permissions.py               # Custom permission classes
│   ├── exceptions.py                # Global exception handler
│   ├── renderers.py                 # Custom JSON response format
│   └── utils/
│       ├── __init__.py
│       └── email.py                 # Helper gửi email
│
├── tasks/                           # Celery tasks (cross-app)
│   ├── __init__.py
│   ├── celery.py                    # Celery app instance
│   └── email_tasks.py
│
├── requirements/
│   ├── base.txt
│   ├── development.txt              # base.txt + debug-toolbar, faker
│   └── production.txt               # base.txt + gunicorn, sentry-sdk
│
├── static/                          # Static files collect (production)
├── media/                           # User-uploaded files
│
├── manage.py
├── .env.example
├── Dockerfile
├── Dockerfile.dev                   # Dev image với hot-reload
└── docker-compose.yml
```

---

## 2. Django Apps

### `apps/users/`
Quản lý thông tin tài khoản người dùng.

**Models:**
- `User` — extends `AbstractBaseUser` + `PermissionsMixin`
  - `email` (unique, login field)
  - `username`
  - `full_name`
  - `avatar` (ImageField)
  - `is_active`, `is_staff`, `is_superuser`
  - `date_joined`

**Services:**
- `create_user(email, password, **kwargs)` → User
- `update_profile(user, data)` → User
- `change_password(user, old_password, new_password)` → void
- `deactivate_user(user_id)` → void

**Selectors:**
- `get_user_by_id(user_id)` → User
- `get_user_by_email(email)` → User
- `list_users(filters)` → QuerySet

---

### `apps/authentication/`
Xử lý JWT, đăng nhập, đăng xuất, reset password.

**Services:**
- `login(email, password)` → `{access, refresh}`
- `logout(refresh_token)` → void (blacklist token)
- `refresh_access_token(refresh_token)` → `{access}`
- `request_password_reset(email)` → void (gửi email)
- `confirm_password_reset(token, new_password)` → void

---

### `apps/core/`
Chứa views không thuộc domain cụ thể:
- `GET /api/health/` — health check (DB + Redis ping)
- `GET /api/v1/` — API root, danh sách endpoints

---

### `common/`
Không phải Django app (không trong `INSTALLED_APPS`). Cung cấp:

**`BaseModel`** — dùng làm base cho mọi model:
```
BaseModel
├── id          UUIDField (primary key)
├── created_at  DateTimeField (auto_now_add)
├── updated_at  DateTimeField (auto_now)
└── is_deleted  BooleanField (default=False) — soft delete
```

**Standard Response Format:**
```json
{
  "data": { ... },
  "message": "Success",
  "errors": null
}
```

**Pagination:**
```json
{
  "data": {
    "count": 100,
    "next": "http://api/v1/users/?page=3",
    "previous": "http://api/v1/users/?page=1",
    "results": [ ... ]
  }
}
```

---

## 3. Layered Architecture

```
Request
   ↓
View (DRF APIView / ViewSet)
   → Validate input qua Serializer
   → Gọi Service (business logic)
       → Service gọi Selector (đọc DB)
       → Service gọi Model methods (ghi DB)
       → Service gọi Celery tasks (async)
   → Serialize output
   ↓
Response
```

| Layer | Quy Tắc Quan Trọng |
|-------|--------------------|
| **View** | Chỉ validate input + gọi service + serialize output |
| **Service** | Business logic — không import request/response |
| **Selector** | Chỉ đọc DB, trả QuerySet hoặc object |
| **Model** | Schema + DB constraints + validators đơn giản |
| **Serializer** | Validate dữ liệu đầu vào, format output |
| **Task** | Logic chạy async (email, export, sync data...) |

---

## 4. Luồng Hoạt Động Chính

### Đăng Ký & Đăng Nhập
```
POST /api/v1/auth/register/
  → AuthRegistrationSerializer.validate()
  → UserService.create_user()
      → User.objects.create_user()
      → Celery: send_welcome_email.delay()
  → Trả 201 + user data

POST /api/v1/auth/login/
  → AuthLoginSerializer.validate()
  → AuthService.login(email, password)
      → authenticate() Django built-in
      → SimpleJWT: generate access + refresh tokens
  → Trả 200 + {access, refresh}
```

### Reset Password
```
POST /api/v1/auth/password-reset/request/
  → Nhận email
  → AuthService.request_password_reset(email)
      → Tạo PasswordResetToken (DB hoặc cache Redis)
      → Celery: send_password_reset_email.delay()
  → Trả 200 "Email đã được gửi"

POST /api/v1/auth/password-reset/confirm/
  → Nhận token + new_password
  → AuthService.confirm_password_reset(token, new_password)
      → Verify token (hết hạn? đã dùng?)
      → user.set_password(new_password)
      → Xóa / invalidate token
  → Trả 200 "Mật khẩu đã đổi thành công"
```

---

## 5. Scaling Considerations

| Vấn Đề | Giải Pháp |
|--------|-----------|
| **Nhiều request đồng thời** | Tăng Gunicorn workers; đặt sau Nginx load balancer |
| **Query DB chậm** | Dùng `select_related` / `prefetch_related`; thêm DB index đúng chỗ |
| **Email / tác vụ nặng** | Đẩy vào Celery task — không block request |
| **Cache data tĩnh** | Redis cache (`@cache_page` hoặc manual cache) |
| **Scale DB** | Read replica PostgreSQL; connection pooling với PgBouncer |
| **Scale Celery** | Tăng số worker container trong docker-compose (replicas) |
| **Nhiều app Django** | Thêm folder trong `apps/` — không ảnh hưởng app khác |

---

## 6. Quy Ước Đặt Tên

| Loại | Quy Ước | Ví Dụ |
|------|---------|-------|
| File service | `<feature>_service.py` | `user_service.py` |
| File selector | `<feature>_selector.py` | `user_selector.py` |
| Class view | `<Resource><Action>View` | `UserListView`, `UserDetailView` |
| Class serializer | `<Model><Purpose>Serializer` | `UserCreateSerializer`, `UserOutputSerializer` |
| Celery task | động từ + danh từ | `send_welcome_email`, `export_report` |
| URL name | `<app>:<resource>-<action>` | `users:user-list`, `users:user-detail` |
