# Django App — Bẫy Thường Gặp & Cách Tránh

## 1. N+1 Query — Bẫy Phổ Biến Nhất

**Vấn đề:** Truy vấn DB trong vòng lặp → 1 query cho list + N query cho mỗi item.

```python
# ❌ N+1 query — với 100 order sẽ chạy 101 queries!
orders = Order.objects.filter(status='pending')
for order in orders:
    print(order.user.email)       # Query DB thêm 1 lần mỗi vòng lặp
    for item in order.items.all():  # Query DB thêm 1 lần nữa
        print(item.product.name)    # Và thêm 1 lần nữa
```

```python
# ✅ Dùng select_related và prefetch_related — chỉ 3 queries dù 1000 orders

orders = (
    Order.objects
    .filter(status='pending')
    .select_related('user')              # JOIN 1-1 hoặc FK → dùng SELECT JOIN
    .prefetch_related('items__product')  # Quan hệ ngược hoặc M2M → dùng IN query
)

for order in orders:
    print(order.user.email)        # Không query thêm
    for item in order.items.all():
        print(item.product.name)   # Không query thêm
```

### Khi Nào Dùng Gì

| Quan hệ | Dùng |
|---------|------|
| `ForeignKey` (forward) | `select_related('field')` |
| `OneToOneField` | `select_related('field')` |
| `ForeignKey` (reverse / related_name) | `prefetch_related('field')` |
| `ManyToManyField` | `prefetch_related('field')` |
| Lồng nhiều cấp | `prefetch_related('items__product__category')` |

### Quy Tắc: Luôn Dùng Selector Cho Queries Phức Tạp

```python
# orders/selectors/order_selector.py

class OrderSelector:
    @staticmethod
    def get_pending_orders_with_details():
        """
        Lấy đơn hàng chờ xử lý kèm đầy đủ thông tin liên quan.
        Dùng prefetch để tránh N+1 query.
        """
        return (
            Order.objects
            .filter(status=OrderStatus.PENDING)
            .select_related('user', 'shipping_address')
            .prefetch_related('items__product__category')
            .order_by('created_at')
        )
```

---

## 2. Circular Import — Lỗi Import Vòng Tròn

**Vấn đề:** App A import App B, App B import App A → `ImportError` hoặc `AppRegistryNotReady`.

```python
# ❌ Circular import
# orders/services/order_service.py
from users.services.user_service import UserService  # import users

# users/services/user_service.py
from orders.services.order_service import OrderService  # import orders — VÒNG TRÒN!
```

### Cách Tránh Circular Import

**Cách 1 — Import trong hàm (lazy import):**
```python
# orders/services/order_service.py
def notify_user_on_order(order):
    """Thông báo user khi có đơn hàng mới."""
    # Import trong hàm thay vì ở đầu file để tránh circular import
    from users.services.notification_service import NotificationService
    NotificationService.send(order.user, f'Đơn hàng #{order.id} đã được tạo')
```

**Cách 2 — Tách logic dùng chung vào `core/`:**
```python
# ❌ orders import users, users import orders
# ✅ Cả orders và users đều import từ core/ — không bao giờ tạo vòng tròn

# core/services/notification_service.py  ← logic chung đặt ở đây
class NotificationService:
    @staticmethod
    def send_to_user(user, message: str) -> None:
        """Gửi thông báo đến user."""
        ...

# orders dùng core
from core.services.notification_service import NotificationService

# users cũng dùng core
from core.services.notification_service import NotificationService
```

**Cách 3 — Dùng Django Signals thay vì import trực tiếp:**
```python
# Thay vì orders import users trực tiếp, dùng signal
# orders/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order

@receiver(post_save, sender=Order)
def on_order_created(sender, instance, created, **kwargs):
    """Khi tạo order mới, phát signal — users app lắng nghe và xử lý."""
    if created:
        from core.services.notification_service import NotificationService
        NotificationService.send_to_user(instance.user, 'Đơn hàng đã được tạo')
```

### Quy Tắc Tránh Circular Import

```
core/       ← Chỉ import từ Django, không import từ app nào khác
   ↑              ↑              ↑
users/      orders/         products/
   (chỉ import từ core, không import lẫn nhau trực tiếp)
```

---

## 3. Soft Delete — Đừng Đặt Tên `delete()`

**Vấn đề:** Đặt tên `soft_delete()` là `delete()` sẽ gây nhầm lẫn với Django's `Model.delete()` thật sự xóa khỏi DB.

```python
# ❌ Nguy hiểm — override delete() gây nhầm lẫn
class SoftDeleteModel(models.Model):
    is_active = models.BooleanField(default=True)

    def delete(self, *args, **kwargs):
        # Ai đọc code này cũng nghĩ đây là xóa thật!
        self.is_active = False
        self.save()

# Khi dùng:
product.delete()  # Xóa thật hay xóa mềm? Không rõ!
```

```python
# ✅ Tên rõ ràng, không nhầm lẫn
class SoftDeleteModel(models.Model):
    is_active = models.BooleanField(default=True)

    def soft_delete(self) -> None:
        """Xóa mềm: đánh dấu inactive, KHÔNG xóa khỏi DB."""
        self.is_active = False
        self.save(update_fields=['is_active'])

    def restore(self) -> None:
        """Khôi phục bản ghi đã bị xóa mềm."""
        self.is_active = True
        self.save(update_fields=['is_active'])

    def hard_delete(self) -> None:
        """Xóa hẳn khỏi DB — dùng cẩn thận."""
        super().delete()

# Khi dùng — đọc là hiểu ngay:
product.soft_delete()   # Rõ ràng: xóa mềm
product.restore()       # Rõ ràng: khôi phục
product.hard_delete()   # Rõ ràng: xóa thật
```

---

## 4. `@transaction.atomic` — Dùng Đúng Chỗ

**Vấn đề:** Quên dùng transaction khi nhiều thao tác DB liên quan nhau → dữ liệu không nhất quán nếu lỗi giữa chừng.

```python
# ❌ Không có transaction — nếu lỗi sau bước 2, order tạo rồi nhưng inventory chưa trừ
def create_order(user, items_data):
    order = Order.objects.create(user=user, status='pending')    # Bước 1
    for item in items_data:
        OrderItem.objects.create(order=order, **item)             # Bước 2
        Product.objects.filter(pk=item['product_id']).update(    # Bước 3
            stock=F('stock') - item['quantity']
        )
    send_confirmation_email(user, order)                          # Bước 4
```

```python
# ✅ Dùng transaction.atomic — tất cả thành công hoặc tất cả rollback
from django.db import transaction

class OrderService:
    @staticmethod
    @transaction.atomic
    def create(user, items_data: list) -> Order:
        """
        Tạo đơn hàng với đầy đủ items và trừ tồn kho.
        Toàn bộ thao tác DB được wrap trong transaction — đảm bảo dữ liệu nhất quán.
        """
        # Tạo order
        order = Order.objects.create(user=user, status=OrderStatus.PENDING)

        # Tạo order items và trừ tồn kho
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            Product.objects.filter(pk=item_data['product_id']).update(
                stock=F('stock') - item_data['quantity']
            )

        # Lưu ý: email gửi bên ngoài transaction
        # vì email không rollback được dù DB rollback
        return order

# Gửi email sau khi transaction thành công, ở tầng view hoặc signal
def create_order_view(request):
    order = OrderService.create(request.user, request.data['items'])
    # Email gửi sau khi transaction đã commit thành công
    send_confirmation_email.delay(request.user.email, order.id)
    return Response(OrderSerializer(order).data, status=201)
```

### Quy Tắc `transaction.atomic`

| Loại thao tác | Có cần transaction? |
|---------------|---------------------|
| Chỉ đọc (SELECT) | Không cần |
| Ghi 1 bảng đơn giản | Không cần (Django tự xử lý) |
| Ghi nhiều bảng liên quan | **Bắt buộc** |
| Tạo object + cập nhật object khác | **Bắt buộc** |
| Gửi email / gọi API bên ngoài | **Không nên đặt trong transaction** |

---

## 5. `select_for_update()` — Tránh Race Condition

Khi check-then-act trên cùng một row (vd: trừ tồn kho), dùng `select_for_update()` để khóa row trong transaction:

```python
from django.db import transaction

@transaction.atomic
def deduct_stock(product_id: int, quantity: int) -> None:
    """
    Trừ tồn kho an toàn, tránh race condition khi nhiều request đồng thời.
    select_for_update() khóa row cho đến khi transaction kết thúc.
    """
    # Khóa row product trong transaction trước khi đọc và cập nhật
    product = Product.objects.select_for_update().get(pk=product_id)

    if product.stock < quantity:
        raise InsufficientStockError(
            f'Tồn kho sản phẩm "{product.name}" không đủ '
            f'(còn {product.stock}, cần {quantity})'
        )

    product.stock -= quantity
    product.save(update_fields=['stock'])
```
