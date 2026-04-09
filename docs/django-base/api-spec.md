# Đặc Tả API Endpoints

> Base URL: `http://localhost:8000/api/v1/`
> Tất cả response theo format chuẩn: `{ "data": ..., "message": ..., "errors": ... }`

---

## 1. Health Check

### `GET /api/health/`

| | |
|--|--|
| **Mục đích** | Kiểm tra server còn sống, DB + Redis có kết nối được không |
| **Permission** | AllowAny |
| **Input** | — |

**Response 200:**
```json
{
  "data": {
    "status": "ok",
    "database": "ok",
    "redis": "ok"
  },
  "message": "Service is healthy"
}
```

**Response 503** (khi DB hoặc Redis lỗi):
```json
{
  "data": {
    "status": "error",
    "database": "error",
    "redis": "ok"
  },
  "message": "Service degraded"
}
```

---

## 2. Authentication

### `POST /api/v1/auth/register/`

| | |
|--|--|
| **Mục đích** | Tạo tài khoản mới |
| **Permission** | AllowAny |

**Input (JSON body):**
```json
{
  "email": "user@example.com",
  "password": "StrongPass123!",
  "password_confirm": "StrongPass123!",
  "full_name": "Nguyen Van A"
}
```

**Validation:**
- `email`: định dạng hợp lệ, chưa tồn tại trong hệ thống
- `password`: tối thiểu 8 ký tự, có chữ hoa, chữ thường, và số
- `password_confirm`: phải khớp với `password`

**Response 201:**
```json
{
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "Nguyen Van A",
    "date_joined": "2026-04-09T10:00:00Z"
  },
  "message": "Tài khoản tạo thành công"
}
```

**Response 400** (validation error):
```json
{
  "data": null,
  "message": "Dữ liệu không hợp lệ",
  "errors": {
    "email": ["Email này đã được sử dụng."],
    "password": ["Mật khẩu quá yếu."]
  }
}
```

---

### `POST /api/v1/auth/login/`

| | |
|--|--|
| **Mục đích** | Đăng nhập, nhận JWT tokens |
| **Permission** | AllowAny |

**Input:**
```json
{
  "email": "user@example.com",
  "password": "StrongPass123!"
}
```

**Response 200:**
```json
{
  "data": {
    "access": "eyJhbGciOiJ...",
    "refresh": "eyJhbGciOiJ...",
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "full_name": "Nguyen Van A"
    }
  },
  "message": "Đăng nhập thành công"
}
```

**Response 401:**
```json
{
  "data": null,
  "message": "Email hoặc mật khẩu không đúng",
  "errors": null
}
```

---

### `POST /api/v1/auth/token/refresh/`

| | |
|--|--|
| **Mục đích** | Lấy access token mới từ refresh token |
| **Permission** | AllowAny |

**Input:**
```json
{ "refresh": "eyJhbGciOiJ..." }
```

**Response 200:**
```json
{
  "data": { "access": "eyJhbGciOiJ..." },
  "message": "Token đã được làm mới"
}
```

---

### `POST /api/v1/auth/logout/`

| | |
|--|--|
| **Mục đích** | Đăng xuất — blacklist refresh token |
| **Permission** | IsAuthenticated |
| **Header** | `Authorization: Bearer <access_token>` |

**Input:**
```json
{ "refresh": "eyJhbGciOiJ..." }
```

**Response 200:**
```json
{
  "data": null,
  "message": "Đăng xuất thành công"
}
```

---

### `POST /api/v1/auth/password/change/`

| | |
|--|--|
| **Mục đích** | Đổi mật khẩu (đã đăng nhập) |
| **Permission** | IsAuthenticated |
| **Header** | `Authorization: Bearer <access_token>` |

**Input:**
```json
{
  "old_password": "OldPass123!",
  "new_password": "NewPass456!",
  "new_password_confirm": "NewPass456!"
}
```

**Response 200:**
```json
{
  "data": null,
  "message": "Mật khẩu đã được cập nhật"
}
```

**Response 400:**
```json
{
  "errors": { "old_password": ["Mật khẩu cũ không đúng."] }
}
```

---

### `POST /api/v1/auth/password/reset/request/`

| | |
|--|--|
| **Mục đích** | Yêu cầu reset mật khẩu — gửi email link/OTP |
| **Permission** | AllowAny |

**Input:**
```json
{ "email": "user@example.com" }
```

**Response 200** (luôn trả 200 dù email có tồn tại hay không — tránh lộ thông tin):
```json
{
  "data": null,
  "message": "Nếu email tồn tại, chúng tôi đã gửi hướng dẫn reset mật khẩu."
}
```

---

### `POST /api/v1/auth/password/reset/confirm/`

| | |
|--|--|
| **Mục đích** | Xác nhận reset — đặt mật khẩu mới |
| **Permission** | AllowAny |

**Input:**
```json
{
  "token": "abc123xyz",
  "new_password": "NewPass456!",
  "new_password_confirm": "NewPass456!"
}
```

**Response 200:**
```json
{
  "data": null,
  "message": "Mật khẩu đã được đặt lại thành công"
}
```

**Response 400:**
```json
{
  "errors": { "token": ["Token không hợp lệ hoặc đã hết hạn."] }
}
```

---

## 3. User Profile

### `GET /api/v1/users/me/`

| | |
|--|--|
| **Mục đích** | Xem thông tin profile của user đang đăng nhập |
| **Permission** | IsAuthenticated |
| **Header** | `Authorization: Bearer <access_token>` |

**Response 200:**
```json
{
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "Nguyen Van A",
    "username": "nguyenvana",
    "avatar": "http://localhost/media/avatars/user.jpg",
    "date_joined": "2026-04-09T10:00:00Z"
  }
}
```

---

### `PATCH /api/v1/users/me/`

| | |
|--|--|
| **Mục đích** | Cập nhật profile (partial update) |
| **Permission** | IsAuthenticated |
| **Header** | `Authorization: Bearer <access_token>` |
| **Content-Type** | `multipart/form-data` (nếu upload avatar) hoặc `application/json` |

**Input (bất kỳ field nào):**
```json
{
  "full_name": "Nguyen Van B",
  "username": "nguyenvanb"
}
```

Hoặc upload avatar:
```
full_name: "Nguyen Van B"
avatar: <file>
```

**Response 200:** trả về user object đã cập nhật

---

## 4. Admin — User Management

> Yêu cầu: `IsAdminUser` (is_staff=True)

### `GET /api/v1/admin/users/`

| | |
|--|--|
| **Mục đích** | Danh sách tất cả user |
| **Permission** | IsAdminUser |
| **Query params** | `search`, `is_active`, `ordering`, `page`, `page_size` |

**Response 200:**
```json
{
  "data": {
    "count": 100,
    "next": "/api/v1/admin/users/?page=2",
    "previous": null,
    "results": [
      {
        "id": "uuid",
        "email": "user@example.com",
        "full_name": "Nguyen Van A",
        "is_active": true,
        "is_staff": false,
        "date_joined": "2026-04-09T10:00:00Z"
      }
    ]
  }
}
```

---

### `GET /api/v1/admin/users/{id}/`

| | |
|--|--|
| **Mục đích** | Xem chi tiết một user |
| **Permission** | IsAdminUser |

---

### `PATCH /api/v1/admin/users/{id}/`

| | |
|--|--|
| **Mục đích** | Cập nhật user (admin có thể thay đổi `is_active`, `is_staff`) |
| **Permission** | IsAdminUser |

**Input:**
```json
{
  "is_active": false
}
```

---

### `DELETE /api/v1/admin/users/{id}/`

| | |
|--|--|
| **Mục đích** | Xóa mềm user (soft delete) — không xóa khỏi DB |
| **Permission** | IsAdminUser |

**Response 204:** No content

---

## 5. Error Codes Chuẩn

| HTTP Status | Ý Nghĩa | Khi Nào Dùng |
|-------------|---------|--------------|
| `200` | OK | Request thành công |
| `201` | Created | Tạo resource mới thành công |
| `204` | No Content | Xóa thành công |
| `400` | Bad Request | Validation error, input sai |
| `401` | Unauthorized | Chưa đăng nhập hoặc token hết hạn |
| `403` | Forbidden | Đăng nhập rồi nhưng không có quyền |
| `404` | Not Found | Resource không tồn tại |
| `409` | Conflict | Duplicate (email đã tồn tại...) |
| `500` | Server Error | Lỗi nội bộ — không để lộ stack trace |

---

## 6. Request Headers

| Header | Bắt Buộc | Ví Dụ |
|--------|----------|-------|
| `Authorization` | Khi cần auth | `Bearer eyJhbGciOiJ...` |
| `Content-Type` | Khi có body | `application/json` |
| `Accept` | Khuyến nghị | `application/json` |
| `Accept-Language` | Tùy chọn | `vi` hoặc `en` |
