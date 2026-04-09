# Django App — Quy Ước Code

## 1. Quy Tắc Độ Dài File — Không Nhồi Code

Khi một file vượt quá **500 dòng**, đó là dấu hiệu file đang đảm nhiệm quá nhiều trách nhiệm. **Bắt buộc tách ra.**

| Ngưỡng | Hành động |
|--------|-----------|
| < 200 dòng | Bình thường |
| 200–500 dòng | Chấp nhận được, theo dõi thêm |
| > 500 dòng | **Tách ngay** thành nhiều file nhỏ hơn |
| > 1000 dòng | Dấu hiệu thiết kế sai, cần refactor cả module |

### Cách Tách Khi Vượt Ngưỡng

```
# ❌ TRƯỚC — một file service chứa tất cả (800 dòng)
orders/services/order_service.py

# ✅ SAU — tách theo từng chức năng
orders/services/
├── __init__.py
├── order_create_service.py    # Chỉ xử lý tạo order
├── order_update_service.py    # Chỉ xử lý cập nhật, hủy order
├── order_query_service.py     # Chỉ xử lý truy vấn, tìm kiếm
└── order_export_service.py    # Chỉ xử lý xuất báo cáo
```

```
# ❌ TRƯỚC — một file model chứa nhiều class (600 dòng)
orders/models/order.py

# ✅ SAU — mỗi model một file riêng
orders/models/
├── __init__.py       # Export tất cả models
├── order.py          # Class Order
├── order_item.py     # Class OrderItem
├── order_status.py   # Class OrderStatus (choices/enum)
└── order_payment.py  # Class OrderPayment
```

---

## 2. Quy Tắc Tái Sử Dụng Code (DRY)

**Nếu một đoạn logic xuất hiện ở 2 nơi trở lên → tách ra một chỗ duy nhất.**

```python
# ❌ KHÔNG làm — copy-paste logic
# order_service.py
def create_order(user, data):
    if not user.is_active:
        raise ValueError('Tài khoản không hoạt động')
    if user.balance < data['total']:
        raise ValueError('Số dư không đủ')

# subscription_service.py — copy y chang!
def create_subscription(user, data):
    if not user.is_active:
        raise ValueError('Tài khoản không hoạt động')
    if user.balance < data['price']:
        raise ValueError('Số dư không đủ')
```

```python
# ✅ NÊN làm — tách ra core/ dùng chung một chỗ

# core/services/user_validation_service.py
class UserValidationService:
    @staticmethod
    def check_can_purchase(user, amount: float) -> None:
        """Kiểm tra user có đủ điều kiện mua hàng không."""
        if not user.is_active:
            raise ValueError('Tài khoản không hoạt động')
        if user.balance < amount:
            raise ValueError('Số dư không đủ')

# order_service.py — tái sử dụng
from core.services.user_validation_service import UserValidationService

def create_order(user, data):
    UserValidationService.check_can_purchase(user, data['total'])

# subscription_service.py — tái sử dụng cùng một chỗ
def create_subscription(user, data):
    UserValidationService.check_can_purchase(user, data['price'])
```

### Quy Tắc Trước Khi Viết Code Mới

Trước khi viết bất kỳ logic nào, hỏi theo thứ tự:

1. **Logic này đã có trong `core/` chưa?** → Nếu có, dùng lại
2. **Logic này đã có trong cùng app chưa?** → Nếu có, import và gọi
3. **Logic này có khả năng dùng ở app khác không?** → Nếu có, đặt vào `core/`
4. **Chỉ khi không có** → mới viết mới, viết đúng chỗ

### Nơi Đặt Code Tái Sử Dụng

| Loại code | Đặt ở đâu |
|-----------|-----------|
| Validators dùng nhiều app | `core/validators/` |
| Services logic dùng chung | `core/services/` |
| Utility functions | `core/utils/` |
| Base models | `core/models/base.py` |
| Permissions dùng chung | `core/permissions/` |
| Mixins cho views | `core/mixins/` |
| Hằng số toàn project | `core/constants.py` |
| Custom exceptions dùng chung | `core/exceptions.py` |

---

## 3. Quy Tắc Đặt Tên

### Bảng Quy Ước

| Loại | Quy tắc | Ví dụ đúng | Ví dụ sai |
|------|---------|-----------|----------|
| Class | `PascalCase`, danh từ | `OrderPaymentService` | `Ops`, `Handler` |
| Function/Method | `snake_case`, động từ | `calculate_discount()` | `discount()`, `doCalc()` |
| Variable | `snake_case`, mô tả rõ | `total_price_after_discount` | `x`, `tmp`, `data2` |
| Constant | `UPPER_SNAKE_CASE` | `MAX_ORDER_QUANTITY` | `max`, `Max` |
| File | `snake_case`, theo chức năng | `order_pricing_service.py` | `service2.py`, `misc.py` |
| Boolean | prefix `is_`, `has_`, `can_` | `is_active`, `has_paid` | `active`, `paid_flag` |
| Soft delete method | `soft_delete()` hoặc `deactivate()` | `product.soft_delete()` | `product.delete()` |

### Đặt Tên Sát Chức Năng

```python
# ❌ Tên mơ hồ — đọc không hiểu làm gì
def process(obj, flag): ...
def handle_data(input): ...
class Manager: ...

# ✅ Tên rõ ràng — đọc là hiểu ngay
def apply_loyalty_discount(order, user_tier: str) -> float:
    """Áp dụng chiết khấu thành viên theo hạng (bronze/silver/gold)."""

def send_order_confirmation_email(order, recipient_email: str) -> None:
    """Gửi email xác nhận đơn hàng đến khách hàng."""

class OrderPricingService:
    """Xử lý toàn bộ logic tính giá và chiết khấu cho đơn hàng."""
```

### Đặt Tên File — Phản Ánh Đúng Nội Dung

```
# ✅ Tên file nói lên vai trò
order_pricing_service.py        # Chỉ chứa logic tính giá
user_authentication_service.py  # Chỉ chứa logic đăng nhập
product_inventory_service.py    # Chỉ chứa logic quản lý kho

# ❌ Tên mơ hồ, không rõ chứa gì
utils.py      # Chứa đủ thứ không liên quan
helpers.py    # Không biết helper cho cái gì
misc.py       # Không có tổ chức
service.py    # Service nào? Làm gì?
```

---

## 4. Ghi Chú Bằng Tiếng Việt

Mọi class, function, và đoạn logic phức tạp **phải có comment tiếng Việt** giải thích mục đích.

```python
# orders/services/order_pricing_service.py

class OrderPricingService:
    """
    Xử lý toàn bộ logic tính giá đơn hàng.
    Bao gồm: giá gốc, chiết khấu, phí vận chuyển, thuế VAT.
    """

    # Ngưỡng tối thiểu để được miễn phí vận chuyển (VNĐ)
    FREE_SHIPPING_THRESHOLD = 500_000

    @staticmethod
    def calculate_total(order_items: list, user) -> dict:
        """
        Tính tổng tiền đơn hàng sau khi áp dụng tất cả ưu đãi.

        Args:
            order_items: Danh sách sản phẩm trong đơn
            user: User đặt hàng (để xác định hạng thành viên)

        Returns:
            dict gồm: subtotal, discount, shipping_fee, tax, total
        """
        # Tính giá gốc trước thuế và giảm giá
        subtotal = sum(item.price * item.quantity for item in order_items)

        # Áp dụng chiết khấu theo hạng thành viên
        discount = OrderPricingService._get_membership_discount(subtotal, user)

        # Tính phí ship: miễn phí nếu đơn hàng trên ngưỡng
        shipping_fee = 0 if subtotal >= OrderPricingService.FREE_SHIPPING_THRESHOLD else 30_000

        # Thuế VAT 10% tính trên giá sau chiết khấu
        taxable_amount = subtotal - discount
        tax = taxable_amount * 0.10

        return {
            'subtotal': subtotal,         # Giá gốc trước giảm
            'discount': discount,         # Số tiền được giảm
            'shipping_fee': shipping_fee, # Phí vận chuyển
            'tax': tax,                   # Thuế VAT
            'total': taxable_amount + tax + shipping_fee,  # Tổng thanh toán
        }
```

---

## 5. `exceptions.py` — Custom Exceptions Per App

**Không dùng `ValueError`, `Exception` thô.** Mỗi app có file exceptions riêng để dễ bắt lỗi chính xác.

```python
# orders/exceptions.py

class OrderNotFoundException(Exception):
    """Không tìm thấy đơn hàng với ID đã cho."""
    pass

class OrderAlreadyCancelledException(Exception):
    """Đơn hàng đã bị hủy, không thể thao tác thêm."""
    pass

class InsufficientBalanceError(Exception):
    """Số dư tài khoản không đủ để thanh toán."""
    pass

class InvalidOrderStatusTransitionError(Exception):
    """Không thể chuyển trạng thái đơn hàng theo yêu cầu."""
    def __init__(self, from_status: str, to_status: str):
        super().__init__(
            f'Không thể chuyển từ trạng thái "{from_status}" sang "{to_status}"'
        )
```

```python
# Dùng trong service
from .exceptions import OrderNotFoundException, InsufficientBalanceError

class OrderService:
    @staticmethod
    def get_by_id(order_id: int) -> Order:
        """Lấy đơn hàng theo ID, raise exception nếu không tìm thấy."""
        try:
            return Order.objects.get(pk=order_id, is_active=True)
        except Order.DoesNotExist:
            raise OrderNotFoundException(f'Không tìm thấy đơn hàng #{order_id}')

# Bắt lỗi chính xác trong view
from .exceptions import OrderNotFoundException

class OrderDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            order = OrderService.get_by_id(pk)
        except OrderNotFoundException as e:
            return Response({'error': str(e)}, status=404)
        return Response(OrderSerializer(order).data)
```

---

## 6. `constants.py` — Hằng Số Per App & Toàn Hệ Thống

### Nhận Diện Magic Value Cần Tách Ra

**Magic value** là bất kỳ string/number cứng nằm trực tiếp trong code. Đây là dấu hiệu cần tạo constants:

```python
# ❌ Dấu hiệu có magic value — cần tách ngay

# Magic string lặp lại ở nhiều nơi
if order.status == 'pending':      # string 'pending' nằm rải rác
if order.status == 'cancelled':    # phải nhớ chính xác spelling

# Magic number không rõ ý nghĩa
if order.total > 500000:           # 500000 là gì? Không ai biết
discount = order.total * 0.10      # 0.10 là thuế? giảm giá? bao nhiêu %?
if len(items) > 50:                # 50 là giới hạn gì?

# String dùng làm config
send_email(to='admin@company.com') # email này thay đổi thì phải sửa bao nhiêu chỗ?
```

### Quy Trình Migration: Thêm Constants Vào Code Đang Có

**Bước 1 — Tìm tất cả magic value trong app:**
Tìm kiếm các string/number xuất hiện hơn 1 lần, hoặc những giá trị quan trọng chỉ xuất hiện 1 lần nhưng có thể thay đổi sau này.

**Bước 2 — Tạo file `constants.py` trong app:**

```python
# orders/constants.py  ← tạo file này trước

class OrderStatus:
    PENDING = 'pending'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'

    CHOICES = [
        (PENDING, 'Chờ xác nhận'),
        (PROCESSING, 'Đang xử lý'),
        (SHIPPED, 'Đã gửi hàng'),
        (DELIVERED, 'Đã giao hàng'),
        (CANCELLED, 'Đã hủy'),
        (REFUNDED, 'Đã hoàn tiền'),
    ]

    CANCELLABLE_STATUSES = [PENDING, PROCESSING]


class PaymentConfig:
    VAT_RATE = 0.10                    # Thuế VAT 10%
    FREE_SHIPPING_THRESHOLD = 500_000  # Miễn ship nếu đơn >= 500k VNĐ
    DEFAULT_SHIPPING_FEE = 30_000      # Phí ship mặc định
    MAX_ITEMS_PER_ORDER = 50           # Tối đa 50 sản phẩm mỗi đơn
```

**Bước 3 — Thay thế magic value trong code cũ:**

```python
# ❌ TRƯỚC — magic value rải rác trong service
def cancel_order(order):
    if order.status not in ['pending', 'processing']:  # magic strings
        raise ValueError('Không thể hủy')
    order.status = 'cancelled'                          # magic string
    order.total = order.total * 0.90                    # magic number không rõ
    order.save()

# ✅ SAU — dùng constants, đọc là hiểu ngay
from .constants import OrderStatus, PaymentConfig

def cancel_order(order):
    """Hủy đơn hàng."""
    if order.status not in OrderStatus.CANCELLABLE_STATUSES:
        raise InvalidOrderStatusTransitionError(order.status, OrderStatus.CANCELLED)
    order.status = OrderStatus.CANCELLED
    order.save(update_fields=['status'])
```

**Bước 4 — Cập nhật model dùng constants cho `choices`:**

```python
# orders/models/order.py
from ..constants import OrderStatus

class Order(models.Model):
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.CHOICES,   # dùng constants thay vì list cứng
        default=OrderStatus.PENDING,   # dùng constants thay vì string 'pending'
    )
```

### Constants Toàn Hệ Thống vs Per App

| Phạm vi | Đặt ở đâu | Khi nào dùng |
|---------|-----------|--------------|
| Dùng trong 1 app | `<app_name>/constants.py` | Chỉ app đó cần |
| Dùng ở 2+ app | `core/constants.py` | Nhiều app share chung |

```python
# core/constants.py — hằng số toàn hệ thống

class UserRole:
    """Role của người dùng trong hệ thống."""
    ADMIN = 'admin'
    STAFF = 'staff'
    CUSTOMER = 'customer'

    CHOICES = [
        (ADMIN, 'Quản trị viên'),
        (STAFF, 'Nhân viên'),
        (CUSTOMER, 'Khách hàng'),
    ]


class PaginationConfig:
    """Cấu hình phân trang mặc định toàn hệ thống."""
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100


class DateTimeFormat:
    """Format ngày giờ dùng chung."""
    DATE = '%d/%m/%Y'
    DATETIME = '%d/%m/%Y %H:%M'
    API_DATE = '%Y-%m-%d'
```

```python
# Cách import đúng — luôn import từ đúng nơi

# Nếu dùng constants của cùng app (relative import)
from .constants import OrderStatus

# Nếu dùng constants từ app khác
from orders.constants import OrderStatus

# Nếu dùng constants toàn hệ thống
from core.constants import UserRole, PaginationConfig
```

### Quy Tắc Đặt Tên Constants

```python
# ✅ Tên đúng chuẩn
class OrderStatus:           # PascalCase — nhóm hằng số liên quan
    PENDING = 'pending'      # UPPER_SNAKE_CASE — giá trị hằng số
    MAX_RETRY = 3            # Rõ ràng: MAX + tên đối tượng
    DEFAULT_TIMEOUT = 30     # Rõ ràng: DEFAULT + tên

# ❌ Tên sai
class order_status:          # Không dùng snake_case cho class
    pending = 'pending'      # Không dùng lowercase cho constant
    x = 3                    # Không có ý nghĩa
    t = 30                   # Không có ý nghĩa
```
