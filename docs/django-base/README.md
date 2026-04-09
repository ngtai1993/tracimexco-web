# Django Base API — Bản Kế Hoạch Dự Án

> Dự án Django REST API chuẩn, chạy trên Docker Desktop, thiết kế để dễ scale và mở rộng.

---

## 1. Tổng Quan

| Mục | Nội Dung |
|-----|----------|
| **Mục đích** | Base template cho mọi dự án Django API — có thể clone và mở rộng theo từng domain |
| **Người dùng hệ thống** | Admin (quản trị nội bộ), Client (người dùng cuối qua API) |
| **Nền tảng** | REST API (JSON) — phục vụ web app, mobile app |
| **Triển khai local** | Docker Desktop (docker compose up) |
| **Thư mục** | `backend/` |

---

## 2. Tech Stack

| Layer | Công Nghệ | Lý Do Chọn |
|-------|-----------|------------|
| **Framework** | Django 5.x + DRF | Mature, ecosystem phong phú, admin miễn phí |
| **Authentication** | `djangorestframework-simplejwt` | JWT stateless, dễ scale |
| **Database** | PostgreSQL 16 | Robust, hỗ trợ JSON field, full-text search |
| **Cache / Message Broker** | Redis 7 | Cache + Celery broker trong một |
| **Async Tasks** | Celery + Celery Beat | Background jobs, scheduled tasks |
| **WSGI Server** | Gunicorn | Production-ready, multi-worker |
| **Reverse Proxy** | Nginx | Static files, SSL termination, load balance |
| **Containerization** | Docker + Docker Compose | Môi trường nhất quán, scale dễ |
| **Filtering** | `django-filter` | Filter querystring chuẩn |
| **Env Management** | `python-decouple` | Tách config khỏi code |

---

## 3. Tính Năng Cốt Lõi (Base)

### Nhóm: Authentication & Authorization
- ✅ Đăng ký tài khoản (email + password)
- ✅ Đăng nhập — trả về JWT access + refresh token
- ✅ Refresh token
- ✅ Đăng xuất (blacklist refresh token)
- ✅ Đổi mật khẩu (đã đăng nhập)
- ✅ Quên mật khẩu + Reset qua email (OTP/link)
- 🔜 Xác thực email sau khi đăng ký
- 🔜 Đăng nhập OAuth (Google, GitHub)

### Nhóm: User Management
- ✅ Xem thông tin profile bản thân
- ✅ Cập nhật profile (tên, avatar, bio)
- ✅ Admin CRUD danh sách user
- ✅ Admin kích hoạt / vô hiệu tài khoản
- 🔜 Phân quyền theo role (RBAC)

### Nhóm: Infrastructure
- ✅ Versioned API (`/api/v1/`)
- ✅ Pagination chuẩn (cursor-based hoặc page-based)
- ✅ Standard response format (`data`, `message`, `errors`)
- ✅ Global exception handler
- ✅ Request logging
- ✅ Health check endpoint
- ✅ Async task với Celery (ví dụ: gửi email)
- 🔜 API rate limiting
- 🔜 Soft delete chung (BaseModel)
- 🔜 Audit log (ai làm gì lúc nào)

---

## 4. Môi Trường & Cấu Hình

| Môi Trường | Mục Đích | File Settings |
|------------|----------|---------------|
| `development` | Local dev với Docker Desktop | `settings/development.py` |
| `staging` | Test trước production | `settings/staging.py` |
| `production` | Deploy thật | `settings/production.py` |

Biến môi trường quản lý qua `.env` file (không commit) + `.env.example` (commit làm tài liệu).

---

## 5. Tài Liệu Liên Quan

| File | Nội Dung |
|------|----------|
| [architecture.md](./architecture.md) | Cấu trúc thư mục, Django apps, layers |
| [docker.md](./docker.md) | Docker services, Compose config, lệnh thường dùng |
| [api-spec.md](./api-spec.md) | Đặc tả API endpoints đầy đủ |
