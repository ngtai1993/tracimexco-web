---
name: django-debug
description: 'Debug dự án Django có hệ thống: đọc traceback, phân tích nguyên nhân gốc rễ, debug từng layer (view → serializer → service → model → DB). Use when: debug lỗi django, fix bug, traceback, 500 error, lỗi API, lỗi database, lỗi validation, lỗi import, lỗi migration, lỗi permission, lỗi celery, debug, tìm nguyên nhân lỗi, phân tích lỗi, xử lý lỗi, fix error.'
argument-hint: 'Mô tả lỗi hoặc paste traceback vào đây (vd: IntegrityError khi tạo user, 500 trên endpoint /api/orders/)'
---

# Django Debug — Phân Tích & Xử Lý Lỗi Có Hệ Thống

Skill này hướng dẫn debug Django một cách bài bản: từ đọc traceback, tìm nguyên nhân gốc rễ, đến fix đúng lớp gây ra lỗi — không đoán mò, không fix tạm thời.

## Khi Nào Dùng
- Gặp exception, traceback, hoặc lỗi 4xx/5xx từ API
- Hành vi không như mong đợi mà không có lỗi rõ ràng (silent bug)
- Lỗi migration, import, Celery task, signal
- Cần hiểu rõ nguyên nhân trước khi sửa

---

## Nguyên Tắc Cốt Lõi

> **Không sửa lỗi mà chưa hiểu nguyên nhân.**
> Mỗi fix phải giải quyết đúng root cause — không patch bề mặt.

1. **Tái hiện lỗi trước** — nếu không tái hiện được, chưa hiểu lỗi
2. **Đọc traceback từ dưới lên** — dòng cuối luôn là điểm gây lỗi trực tiếp
3. **Khoanh vùng layer gây lỗi** — đừng debug toàn bộ codebase cùng lúc
4. **Kiểm tra giả thuyết** — đặt câu hỏi "nếu X thì Y" rồi dùng tool/log kiểm chứng
5. **Fix một chỗ, verify lại** — không sửa nhiều nơi cùng lúc

---

## Quy Trình 5 Bước

### Bước 1 — Thu Thập Thông Tin Lỗi

Yêu cầu người dùng cung cấp:
- **Full traceback** (không cắt bớt)
- **Endpoint hoặc command** gây ra lỗi
- **Dữ liệu đầu vào** (request body, params, user context)
- **Môi trường** (development / production / testing)
- **Lỗi xuất hiện lúc nào** (luôn luôn? thỉnh thoảng? sau khi deploy?)

Nếu không có traceback, hướng dẫn lấy log:
```bash
# Xem log Django (development)
python manage.py runserver  # lỗi in thẳng ra terminal

# Xem log Celery
celery -A config worker --loglevel=debug

# Xem log trong shell
python manage.py shell_plus
```

### Bước 2 — Đọc & Phân Tích Traceback

#### Cách Đọc Traceback Django

```
Traceback (most recent call last):            ← BẮT ĐẦU từ đây (entry point)
  File "users/views/auth_views.py", line 45   ← Layer ngoài cùng
    response = auth_service.login(data)
  File "users/services/auth_service.py", line 23
    user = User.objects.get(email=email)
  File "django/db/models/query.py", line 637  ← Django internals (thường bỏ qua)
    raise self.model.DoesNotExist(...)
users.models.User.DoesNotExist: ...           ← ĐỌC DÒNG NÀY TRƯỚC (root error)
```

**Quy tắc đọc:**
- Dòng **cuối cùng** = exception type + message → đọc đầu tiên
- Dòng **gần cuối** trong code của dự án = nơi gây lỗi (bỏ qua django internals)
- Dòng **đầu tiên** = entry point (view, management command, task)

#### Nhận Diện Exception Type Phổ Biến

| Exception | Nguyên nhân thường gặp |
|-----------|----------------------|
| `DoesNotExist` | Query `.get()` không tìm thấy object |
| `MultipleObjectsReturned` | Query `.get()` trả về nhiều hơn 1 object |
| `IntegrityError` | Vi phạm unique constraint, NOT NULL, FK |
| `ValidationError` | Dữ liệu không hợp lệ (model hoặc serializer) |
| `PermissionDenied` | User không có quyền truy cập |
| `ImproperlyConfigured` | Cấu hình settings/app sai |
| `AttributeError` | Truy cập attribute không tồn tại (None object?) |
| `KeyError` | Truy cập key không có trong dict |
| `TypeError` | Sai kiểu dữ liệu hoặc sai số lượng argument |
| `ImportError / ModuleNotFoundError` | Module không tồn tại hoặc circular import |
| `OperationalError` | Lỗi DB connection, missing migration |
| `ProgrammingError` | Column/table không tồn tại (chưa migrate) |

### Bước 3 — Khoanh Vùng Layer Gây Lỗi

Debug theo kiến trúc từ ngoài vào trong:

```
Request
  └── [URL Router] → urls.py
        └── [View Layer] → views/
              └── [Serializer] → serializers/
                    └── [Service Layer] → services/
                          └── [Selector / Query] → selectors/
                                └── [Model] → models/
                                      └── [Database]
```

**Chiến lược khoanh vùng:**

1. Lỗi xảy ra **trước khi vào service** → kiểm tra View, Serializer, Permission
2. Lỗi xảy ra **trong service** → kiểm tra business logic, data validation
3. Lỗi xảy ra **khi query DB** → kiểm tra Selector, Model, Migration
4. Lỗi **không có traceback** (silent) → kiểm tra response data, log thủ công

**Kỹ thuật khoanh vùng nhanh:**

```python
# Thêm print/log tạm để xác định data tại mỗi điểm
import logging
logger = logging.getLogger(__name__)

def some_service(data):
    logger.debug("Input data: %s", data)        # Kiểm tra input
    result = some_query(data['user_id'])
    logger.debug("Query result: %s", result)   # Kiểm tra sau query
    return process(result)
```

### Bước 4 — Phân Tích Nguyên Nhân Gốc Rễ (Root Cause Analysis)

Sau khi khoanh vùng được layer, đặt câu hỏi "Tại sao?" liên tục (5 Whys):

```
Lỗi: IntegrityError — NOT NULL constraint failed: orders_order.user_id
  → Tại sao user_id là NULL?
    → Tại sao user không được gán?
      → Tại sao service không nhận user từ request?
        → Tại sao view không truyền request.user vào service?
          → ROOT CAUSE: View gọi service thiếu tham số user
```

**Checklist phân tích theo loại lỗi:**

#### Lỗi Database
```python
# Kiểm tra migration
python manage.py showmigrations
python manage.py migrate --check

# Kiểm tra schema thực tế
python manage.py dbshell
> \d table_name  # PostgreSQL
> DESCRIBE table_name;  # MySQL

# Kiểm tra dữ liệu gây lỗi
python manage.py shell_plus
>>> User.objects.filter(email=email).count()  # Kiểm tra duplicate
>>> Order.objects.filter(pk=order_id).exists()  # Kiểm tra tồn tại
```

#### Lỗi Serializer / Validation
```python
# Debug serializer errors
serializer = OrderSerializer(data=request_data)
if not serializer.is_valid():
    print(serializer.errors)  # Dict chi tiết field nào sai
    
# Kiểm tra field required
print(serializer.fields)
print({k: v.required for k, v in serializer.fields.items()})
```

#### Lỗi Permission / Authentication
```python
# Kiểm tra view permission classes
print(view.permission_classes)

# Kiểm tra user context trong shell
from rest_framework.test import APIRequestFactory
factory = APIRequestFactory()
request = factory.post('/endpoint/', data)
print(request.user)  # AnonymousUser nếu chưa auth
```

#### Lỗi Celery Task
```bash
# Chạy task đồng bộ để xem lỗi trực tiếp
python manage.py shell_plus
>>> from tasks import my_task
>>> my_task.apply(args=[...])  # Chạy sync, in traceback đầy đủ
```

#### Lỗi Import / Circular Import
```bash
# Kiểm tra import chain
python -c "import your_module"  # Xem lỗi trực tiếp

# Circular import — dấu hiệu: ImportError khi import model
# Fix: chuyển import vào trong function, dùng apps.get_model()
from django.apps import apps
User = apps.get_model('users', 'User')
```

### Bước 5 — Fix, Verify, Phòng Ngừa

#### Trước Khi Fix
- [ ] Đã biết chính xác dòng code gây lỗi
- [ ] Đã hiểu nguyên nhân gốc rễ (không phải triệu chứng)
- [ ] Biết fix ở layer nào là đúng nhất

#### Implement Fix

Fix đúng layer:
- Lỗi logic nghiệp vụ → fix trong **service**
- Lỗi dữ liệu đầu vào → fix trong **serializer**
- Lỗi DB constraint → fix **model + migration**
- Lỗi quyền truy cập → fix trong **permission class**
- Lỗi cấu hình → fix trong **settings**

#### Verify Fix
```bash
# Chạy test liên quan
python manage.py test users.tests.test_auth_service -v 2

# Test thủ công qua API
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "secret"}'

# Kiểm tra không có regression
python manage.py test  # Toàn bộ test suite
```

#### Viết Test Để Phòng Ngừa
```python
# Viết test bắt đúng case gây ra lỗi ban đầu
def test_create_order_without_user_raises_error():
    """Regression test: đảm bảo lỗi IntegrityError không tái hiện."""
    with pytest.raises(ValidationError):
        OrderService.create_order(user=None, items=[...])
```

---

## Công Cụ Debug Django

### Django Shell
```bash
python manage.py shell_plus  # shell với auto-import models (django-extensions)
python manage.py shell       # shell chuẩn
```

### Django Logging (settings)
```python
# settings/development.py — bật debug log chi tiết
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'DEBUG'},
        'django.db.backends': {'handlers': ['console'], 'level': 'DEBUG'},  # In SQL queries
    },
}
```

### Kiểm Tra SQL Query Sinh Ra
```python
from django.db import connection, reset_queries
from django.conf import settings

settings.DEBUG = True
reset_queries()

# Chạy code cần kiểm tra
queryset.filter(...).all()

# In toàn bộ queries
for q in connection.queries:
    print(q['sql'])
```

### Django Debug Toolbar
```python
# Cài trong development.txt
django-debug-toolbar

# settings/development.py
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']
```

---

## Các Lỗi Phổ Biến Trong Dự Án Này

### Pattern: Service nhận sai kiểu dữ liệu
```python
# ❌ View truyền raw request data
UserService.update_profile(data=request.data)

# ✅ View truyền validated data từ serializer
serializer = ProfileSerializer(data=request.data)
serializer.is_valid(raise_exception=True)
UserService.update_profile(data=serializer.validated_data, user=request.user)
```

### Pattern: Query trả về None thay vì raise exception
```python
# ❌ .filter().first() trả về None → AttributeError ở bước sau
user = User.objects.filter(email=email).first()
user.is_active  # AttributeError: 'NoneType' object has no attribute 'is_active'

# ✅ Dùng get_object_or_404 hoặc raise explicitly
from django.shortcuts import get_object_or_404
user = get_object_or_404(User, email=email)
# hoặc trong service:
try:
    user = User.objects.get(email=email)
except User.DoesNotExist:
    raise UserNotFound(f"User with email {email} not found")
```

### Pattern: Celery task không nhận context user
```python
# ❌ Pass cả object vào task (không serialize được)
send_email_task.delay(user=user_object)

# ✅ Pass ID, query lại trong task
send_email_task.delay(user_id=user.id)

@shared_task
def send_email_task(user_id):
    user = User.objects.get(pk=user_id)
    ...
```

### Pattern: Migration conflict
```bash
# Phát hiện
python manage.py migrate --check  # Báo unapplied migrations

# Xử lý conflict (khi merge branch)
python manage.py makemigrations --merge
python manage.py migrate
```
