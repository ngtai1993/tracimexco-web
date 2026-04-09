# Django App — Kiến Trúc & Mở Rộng

## Nguyên Tắc Cốt Lõi

### 1. Separation of Concerns (Tách Biệt Trách Nhiệm)

```
Request → View → Service → Model → DB
              ↑         ↑
         (gọi service) (chỉ data schema)

         Selector ────────────────┘
         (chỉ đọc DB, trả queryset)
```

| Layer | Trách Nhiệm | KHÔNG được làm |
|-------|-------------|----------------|
| `views/` | Nhận request, gọi service/selector, trả response | Chứa logic nghiệp vụ |
| `services/` | Business logic: tạo, cập nhật, xử lý nghiệp vụ | Truy cập request/response object |
| `selectors/` | Truy vấn DB, lọc, annotate — chỉ đọc | Write vào DB |
| `models/` | Định nghĩa schema, quan hệ, validators cơ bản | Business logic phức tạp |
| `serializers/` | Validate input, serialize output | Business logic |

### 2. Fat Service, Thin View

```python
# ❌ KHÔNG làm — logic trong view
def create_order(request):
    items = request.data['items']
    total = sum(item['price'] * item['qty'] for item in items)
    if total > 10000:
        discount = total * 0.1
    order = Order.objects.create(total=total - discount, ...)
    send_email(request.user.email, order)
    return Response(...)

# ✅ NÊN làm — gọi service
def create_order(request):
    order = OrderService.create(request.user, request.data)
    return Response(OrderSerializer(order).data, status=201)
```

### 3. Selectors — Tách Riêng Logic Đọc DB

Khi queries phức tạp (filter, annotate, prefetch), **không** để trong service, tách vào `selectors/`:

```python
# orders/selectors/order_selector.py

class OrderSelector:
    @staticmethod
    def get_active_orders_for_user(user):
        """Lấy danh sách đơn hàng đang hoạt động của user, kèm thông tin sản phẩm."""
        return (
            Order.objects
            .filter(user=user, status__in=['pending', 'processing'])
            .select_related('user')          # tránh N+1 với user
            .prefetch_related('items__product')  # tránh N+1 với items
            .order_by('-created_at')
        )

    @staticmethod
    def get_revenue_by_month(year: int):
        """Thống kê doanh thu theo tháng trong năm."""
        from django.db.models import Sum
        from django.db.models.functions import TruncMonth
        return (
            Order.objects
            .filter(created_at__year=year, status='completed')
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total_revenue=Sum('total'))
            .order_by('month')
        )
```

```python
# orders/views/order_views.py — dùng selector để đọc, service để ghi
from ..selectors.order_selector import OrderSelector
from ..services.order_service import OrderService

class OrderListAPIView(APIView):
    def get(self, request):
        # Đọc → dùng selector
        orders = OrderSelector.get_active_orders_for_user(request.user)
        return Response(OrderSerializer(orders, many=True).data)

    def post(self, request):
        # Ghi → dùng service
        order = OrderService.create(request.user, request.data)
        return Response(OrderSerializer(order).data, status=201)
```

---

## Mở Rộng Theo Tính Năng (Feature-based)

Khi một app phình to, tổ chức theo tính năng trong từng folder:

```
orders/
├── models/
│   ├── __init__.py
│   ├── order.py                 # Model Order
│   └── order_item.py            # Model OrderItem
│
├── views/
│   ├── __init__.py
│   ├── order_views.py           # CRUD cho Order
│   └── checkout_views.py        # Checkout flow
│
├── services/
│   ├── __init__.py
│   ├── order_service.py         # Tạo, cập nhật order
│   ├── pricing_service.py       # Tính toán giá, discount
│   └── notification_service.py  # Gửi email, push
│
├── selectors/
│   ├── __init__.py
│   ├── order_selector.py        # Queries đọc cho Order
│   └── report_selector.py       # Queries thống kê, báo cáo
│
├── serializers/
│   ├── __init__.py
│   ├── order_serializer.py
│   └── checkout_serializer.py
│
└── tests/
    ├── test_order_service.py
    ├── test_order_selector.py
    └── test_pricing_service.py
```

---

## Tách App Khi Nào?

| Dấu hiệu | Hành động |
|----------|-----------|
| Services > 5 file | Cân nhắc tách thành sub-app |
| Models không liên quan nhau | Tách app riêng |
| Team > 3 người cùng sửa 1 app | Tách theo domain |
| App có thể dùng độc lập | Tách thành package |

---

## Shared Logic Giữa Các Apps — App `core/`

Tạo app `core/` cho tất cả code dùng chung toàn project:

```
core/
├── __init__.py
├── apps.py
├── constants.py             # Hằng số dùng toàn project
├── exceptions.py            # Custom exceptions dùng chung
├── models/
│   ├── __init__.py
│   └── base.py              # TimeStampedModel, SoftDeleteModel
├── services/
│   ├── __init__.py
│   ├── email_service.py     # Gửi email dùng chung
│   └── file_service.py      # Xử lý upload/download file
├── validators/
│   ├── __init__.py
│   └── common_validators.py # Validate phone, email, ngày tháng
├── utils/
│   ├── __init__.py
│   ├── pagination.py        # Pagination helper
│   └── date_utils.py        # Tiện ích xử lý ngày tháng
├── permissions/
│   ├── __init__.py
│   └── role_permissions.py  # Permission theo role
└── mixins/
    ├── __init__.py
    └── view_mixins.py       # Mixin dùng lại cho views
```

### BaseModel dùng chung

```python
# core/models/base.py
from django.db import models


class TimeStampedModel(models.Model):
    """Base model tự động lưu thời gian tạo và cập nhật."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(TimeStampedModel):
    """Base model hỗ trợ xóa mềm — không xóa khỏi DB, chỉ đánh dấu inactive."""
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        """Xóa mềm: đánh dấu inactive thay vì xóa khỏi DB."""
        self.is_active = False
        self.save(update_fields=['is_active'])

    def restore(self) -> None:
        """Khôi phục bản ghi đã bị xóa mềm."""
        self.is_active = True
        self.save(update_fields=['is_active'])
```

---

## Signals — Tổ Chức Đúng Cách

```python
# <app_name>/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order


@receiver(post_save, sender=Order)
def on_order_created(sender, instance, created, **kwargs):
    """Khi tạo order mới, gửi email xác nhận cho khách hàng."""
    if created:
        # Import trong hàm để tránh circular import
        from .services.notification_service import NotificationService
        NotificationService.send_order_confirmation(instance)
```

Đăng ký trong `apps.py`:
```python
def ready(self):
    import <app_name>.signals  # noqa
```

---

## Environment & Settings

Tổ chức settings theo môi trường:

```
project/
└── settings/
    ├── __init__.py
    ├── base.py         # Cài đặt chung cho mọi môi trường
    ├── development.py  # Ghi đè cho local dev (DEBUG=True, SQLite...)
    ├── production.py   # Ghi đè cho production (HTTPS, PostgreSQL...)
    └── testing.py      # Ghi đè cho chạy test (DB in-memory...)
```
