---
name: django-new-app
description: 'Tạo Django app mới với cấu trúc folder chuẩn, dễ mở rộng. Use when: tạo app Django, django new app, cấu trúc django, django app structure, django folder, thêm app vào django project, django scalable, django services views models folder.'
argument-hint: 'Tên app cần tạo (vd: products, orders, users)'
---

# Django New App — Cấu Trúc Chuẩn

Skill này hướng dẫn tạo một Django app mới với cấu trúc folder rõ ràng, dễ quản lý và mở rộng theo mô hình **MTV + Service Layer**.

## Khi Nào Dùng
- Thêm một app mới vào Django project
- Cần chuẩn hóa lại cấu trúc folder của app hiện tại
- Muốn tách biệt logic nghiệp vụ (services) ra khỏi views

## Cấu Trúc App Chuẩn

```
<app_name>/
├── __init__.py
├── apps.py
├── urls.py
├── admin.py
├── signals.py
│
├── models/
│   ├── __init__.py          # export tất cả models
│   └── <model_name>.py
│
├── views/
│   ├── __init__.py          # export tất cả views
│   └── <feature>_views.py
│
├── services/
│   ├── __init__.py
│   └── <feature>_service.py # Business logic: tạo, cập nhật, xử lý nghiệp vụ
│
├── selectors/               # Truy vấn DB phức tạp — chỉ đọc
│   ├── __init__.py
│   └── <feature>_selector.py
│
├── serializers/             # Nếu dùng DRF
│   ├── __init__.py
│   └── <model_name>_serializer.py
│
├── forms/                   # Nếu dùng Django Forms
│   ├── __init__.py
│   └── <feature>_form.py
│
├── exceptions.py            # Custom exceptions của app này
├── constants.py             # Hằng số, choices, enums của app này
│
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_services.py
│   └── test_selectors.py
│
├── migrations/
│   └── __init__.py
│
├── templates/
│   └── <app_name>/
│       └── base.html
│
└── static/
    └── <app_name>/
        ├── css/
        ├── js/
        └── img/
```

## Quy Tắc Quan Trọng

| Layer | Trách Nhiệm | KHÔNG được làm |
|-------|-------------|----------------|
| `models/` | Định nghĩa data schema, quan hệ DB, validators cơ bản | Business logic phức tạp |
| `views/` | Nhận request, gọi service/selector, trả response | Logic nghiệp vụ trực tiếp |
| `services/` | Business logic: tạo, cập nhật, xử lý nghiệp vụ | Truy cập request/response object |
| `selectors/` | Truy vấn DB, filter, annotate — chỉ đọc | Write vào DB |
| `serializers/` | Validate input, serialize output (DRF) | Business logic |
| `forms/` | Validate HTML form data | Business logic |

## Procedure

### Bước 1 — Tạo App Django
```bash
python manage.py startapp <app_name>
```

### Bước 2 — Chuyển đổi sang cấu trúc folder

Thay thế `models.py` và `views.py` mặc định bằng folder:

```bash
# Xóa file mặc định, tạo folder
rm models.py views.py
mkdir models views services serializers forms tests
```

Tạo `__init__.py` trong mỗi folder.

### Bước 3 — Cấu hình `apps.py`

```python
# <app_name>/apps.py
from django.apps import AppConfig

class <AppName>Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '<app_name>'

    def ready(self):
        import <app_name>.signals  # noqa
```

### Bước 4 — Đăng ký app vào `settings.py`

```python
INSTALLED_APPS = [
    ...
    '<app_name>.apps.<AppName>Config',
]
```

### Bước 5 — Cấu hình `urls.py` của app

```python
# <app_name>/urls.py
from django.urls import path
from .views import <FeatureView>

app_name = '<app_name>'

urlpatterns = [
    path('', <FeatureView>.as_view(), name='list'),
]
```

### Bước 6 — Include vào project `urls.py`

```python
# project/urls.py
from django.urls import path, include

urlpatterns = [
    path('<app_name>/', include('<app_name>.urls', namespace='<app_name>')),
]
```

### Bước 7 — Tạo Migration

```bash
python manage.py makemigrations <app_name>
python manage.py migrate
```

## Templates Code Chuẩn

Xem chi tiết tại [references/templates.md](./references/templates.md)

## Kiến Trúc & Mở Rộng

Xem quy tắc tổ chức, tách app, selectors layer tại [references/scalability.md](./references/scalability.md)

## Quy Ước Code

Xem quy tắc đặt tên, DRY, độ dài file, comment, exceptions, constants tại [references/conventions.md](./references/conventions.md)

## Bẫy Thường Gặp

Xem N+1 query, circular import, soft delete, transaction tại [references/pitfalls.md](./references/pitfalls.md)

## Serializers

Xem nguyên tắc viết serializer, tách read/write, áp dụng vào views tại [references/serializers.md](./references/serializers.md)

## Testing

Xem cách viết test cho models, services, selectors, API endpoints tại skill `/django-testing`

## Checklist Hoàn Thành

**Cấu trúc**
- [ ] App đã được thêm vào `INSTALLED_APPS`
- [ ] `models/__init__.py` export đúng tất cả models
- [ ] `views/__init__.py` export đúng tất cả views
- [ ] `urls.py` có `app_name` (namespace)
- [ ] Đã include urls vào project `urls.py`
- [ ] `migrations/` folder tồn tại với `__init__.py`
- [ ] `signals.py` đã được đăng ký trong `apps.py ready()`

**Tổ chức code**
- [ ] Business logic nằm trong `services/`, không nằm trong `views/`
- [ ] Queries phức tạp nằm trong `selectors/`, không trong `services/`
- [ ] Không có magic string/number — dùng `constants.py`
- [ ] Không dùng `ValueError`/`Exception` thô — dùng `exceptions.py`
- [ ] Không có method nào đặt tên `delete()` cho soft-delete
- [ ] Không có file nào vượt 500 dòng
- [ ] Không có logic nào bị copy-paste ở 2 nơi trở lên

**Serializers (nếu dùng DRF)**
- [ ] Write serializer (input) và Read serializer (output) được tách riêng
- [ ] Output serializer có `read_only_fields` khai báo đầy đủ
- [ ] Views dùng `serializer.validated_data` → truyền vào service — không dùng `serializer.save()`
- [ ] Không có business logic trong serializer
- [ ] Nested serializer đi kèm `select_related`/`prefetch_related` trong selector
- [ ] `serializers/__init__.py` export đầy đủ

**Constants**
- [ ] Không có magic string/number — dùng `constants.py`
- [ ] Constants dùng nhiều app được đặt vào `core/constants.py`
- [ ] Tên constants đúng chuẩn: class `PascalCase`, giá trị `UPPER_SNAKE_CASE`

**Chất lượng**
- [ ] Mọi class và method có docstring tiếng Việt
- [ ] Queries có `select_related`/`prefetch_related` khi join model liên quan
- [ ] Các thao tác ghi nhiều bảng được wrap trong `@transaction.atomic`
- [ ] Tests được tổ chức theo từng layer (models, services, selectors, views)
