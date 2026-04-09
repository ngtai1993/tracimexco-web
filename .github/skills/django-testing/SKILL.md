---
name: django-testing
description: 'Viết test cho Django app: unit test models/services/selectors, integration test, API test với DRF. Use when: viết test, test django, test API, test service, kiểm tra logic, pytest django, unittest, test endpoint, đảm bảo chức năng đúng, test coverage.'
argument-hint: 'Tên app hoặc tính năng cần test (vd: orders, product service, checkout API)'
---

# Django Testing — Nguyên Tắc & Quy Trình Test

Skill này hướng dẫn viết test đầy đủ cho Django app: từ unit test từng layer (models, services, selectors) đến integration test API endpoints — đảm bảo mọi tính năng hoạt động đúng logic.

## Khi Nào Dùng
- Viết test cho app hoặc tính năng mới
- Kiểm tra service có xử lý đúng logic nghiệp vụ không
- Đảm bảo API endpoint trả đúng response, đúng status code
- Kiểm tra edge case và error handling
- Trước khi merge code — chạy lại toàn bộ test suite

---

## Nguyên Tắc Testing

### Test Pyramid — Ưu Tiên Theo Tầng

```
         /\
        /  \  ← API / Integration Tests (ít, chậm, chi phí cao)
       /----\
      /      \ ← Service / Selector Tests (vừa phải)
     /--------\
    /          \ ← Unit Tests: Model, Validator, Util (nhiều, nhanh, rẻ)
   /____________\
```

- **Viết nhiều unit test** — nhanh, tập trung, dễ debug
- **Viết vừa đủ service test** — test business logic cốt lõi
- **Viết API test cho mỗi endpoint** — ít nhất: happy path + 1-2 error cases

### Mỗi Test Chỉ Kiểm Tra Một Điều

```python
# ❌ Một test làm quá nhiều — khó biết cái gì fail
def test_order():
    order = create_order(...)
    assert order.status == 'pending'
    assert order.total == 150000
    assert order.items.count() == 2
    assert email_was_sent()
    assert stock_was_deducted()

# ✅ Mỗi test một mục đích rõ ràng
def test_new_order_has_pending_status(): ...
def test_order_total_calculated_correctly(): ...
def test_order_confirmation_email_sent(): ...
def test_stock_deducted_after_order_created(): ...
```

### Đặt Tên Test Rõ Ràng

```python
# ❌ Tên không biết test gì
def test_order(): ...
def test_service(): ...
def test_1(): ...

# ✅ Tên = mô tả điều kiện + kết quả mong đợi
def test_create_order_with_insufficient_stock_raises_error(): ...
def test_cancel_order_restores_product_stock(): ...
def test_inactive_user_cannot_create_order(): ...
```

### Cấu Trúc Test: Arrange — Act — Assert (AAA)

```python
def test_apply_gold_membership_discount():
    # Arrange — chuẩn bị dữ liệu
    user = UserFactory(membership_tier='gold')
    order_total = 1_000_000

    # Act — thực hiện hành động cần test
    discount = OrderPricingService.calculate_discount(order_total, user)

    # Assert — kiểm tra kết quả
    assert discount == 100_000  # gold = 10% discount
```

---

## Cấu Trúc Folder Tests

```
<app_name>/tests/
├── __init__.py
├── factories.py          # Factory Boy — tạo test data nhanh
├── test_models.py        # Test model validators, methods, constraints
├── test_services.py      # Test business logic trong services
├── test_selectors.py     # Test queries, filter, annotate
├── test_views.py         # Test API endpoints (DRF APIClient)
└── test_serializers.py   # Test serializer validation (tuỳ chọn)
```

---

## Công Cụ Sử Dụng

| Công cụ | Mục đích |
|---------|---------|
| `django.test.TestCase` | Base class, tự rollback DB sau mỗi test |
| `rest_framework.test.APIClient` | Gửi request đến DRF API |
| `factory_boy` | Tạo test data linh hoạt, không hardcode |
| `pytest-django` | Chạy test bằng pytest (tuỳ chọn, nhanh hơn) |
| `unittest.mock.patch` | Mock external services (email, payment...) |

---

## Procedure

### Bước 1 — Tạo Factories Trước

Tạo `tests/factories.py` — dùng để tạo test data nhất quán, không lặp code setup:

```python
# <app_name>/tests/factories.py
import factory
from factory.django import DjangoModelFactory
from ..models import Product, Order, OrderItem

class UserFactory(DjangoModelFactory):
    """Tạo user test với dữ liệu tự động."""
    class Meta:
        model = 'auth.User'

    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    is_active = True

class ProductFactory(DjangoModelFactory):
    """Tạo sản phẩm test."""
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f'Sản phẩm {n}')
    slug = factory.Sequence(lambda n: f'san-pham-{n}')
    price = 100_000
    stock = 50
    is_active = True

class OrderFactory(DjangoModelFactory):
    """Tạo đơn hàng test."""
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    status = 'pending'
    total = 200_000
```

### Bước 2 — Test Models

Xem chi tiết tại [references/unit-tests.md](./references/unit-tests.md)

### Bước 3 — Test Services & Selectors

Xem chi tiết tại [references/unit-tests.md](./references/unit-tests.md)

### Bước 4 — Test API Endpoints

Xem chi tiết tại [references/api-tests.md](./references/api-tests.md)

### Bước 5 — Chạy Test & Kiểm Tra Coverage

```bash
# Chạy tất cả tests
python manage.py test

# Chạy test của một app
python manage.py test orders

# Chạy một test class
python manage.py test orders.tests.test_services.OrderServiceTestCase

# Chạy một test cụ thể
python manage.py test orders.tests.test_services.OrderServiceTestCase.test_cancel_order_restores_stock

# Dùng pytest (nhanh hơn, output đẹp hơn)
pytest
pytest orders/tests/
pytest orders/tests/test_services.py -v
pytest -k "test_cancel"   # lọc theo tên

# Kiểm tra coverage
pytest --cov=orders --cov-report=term-missing
```

---

## Checklist Trước Khi Merge

**Unit Tests**
- [ ] Mỗi service method có ít nhất 1 happy path test
- [ ] Mỗi service method có test cho trường hợp lỗi (exception)
- [ ] Model constraints (unique, max_length) được test
- [ ] Selectors trả đúng dữ liệu khi có filter

**API Tests**
- [ ] Mỗi endpoint có test: 200/201 happy path
- [ ] Endpoint cần auth trả 401 khi chưa đăng nhập
- [ ] Endpoint trả 400 khi input sai / thiếu field bắt buộc
- [ ] Endpoint trả 404 khi resource không tồn tại
- [ ] Endpoint trả 403 khi không có quyền

**Chất Lượng**
- [ ] Không có test nào phụ thuộc vào thứ tự chạy
- [ ] External services (email, payment) được mock
- [ ] Không hardcode ID — dùng factory để tạo object
- [ ] Tên test mô tả rõ điều kiện và kết quả
