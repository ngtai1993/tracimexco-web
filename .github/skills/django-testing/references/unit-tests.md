# Unit Tests — Models, Services, Selectors

## 1. Test Models

Test những gì model tự làm: validators, custom methods, constraints DB.

```python
# orders/tests/test_models.py

from django.test import TestCase
from django.core.exceptions import ValidationError
from .factories import OrderFactory, ProductFactory, UserFactory
from ..models import Order
from ..constants import OrderStatus


class OrderModelTest(TestCase):

    def test_str_returns_order_id(self):
        """__str__ phải trả về định danh dễ đọc của đơn hàng."""
        order = OrderFactory(id=42)
        self.assertIn('42', str(order))

    def test_new_order_default_status_is_pending(self):
        """Đơn hàng mới tạo phải có trạng thái mặc định là pending."""
        order = OrderFactory()
        self.assertEqual(order.status, OrderStatus.PENDING)

    def test_soft_delete_sets_is_active_false(self):
        """Soft delete phải đánh dấu is_active=False, không xóa khỏi DB."""
        order = OrderFactory()
        order_id = order.id

        order.soft_delete()

        # Vẫn còn trong DB
        self.assertTrue(Order.objects.filter(id=order_id).exists())
        # Nhưng is_active = False
        order.refresh_from_db()
        self.assertFalse(order.is_active)

    def test_restore_sets_is_active_true(self):
        """Khôi phục bản ghi đã soft delete."""
        order = OrderFactory(is_active=False)
        order.restore()
        order.refresh_from_db()
        self.assertTrue(order.is_active)


class ProductModelTest(TestCase):

    def test_name_cannot_be_blank(self):
        """Tên sản phẩm không được để trống."""
        product = ProductFactory.build(name='')
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_price_must_be_positive(self):
        """Giá sản phẩm phải lớn hơn 0."""
        product = ProductFactory.build(price=-1)
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_slug_must_be_unique(self):
        """Slug phải là duy nhất trong toàn bộ bảng."""
        from django.db import IntegrityError
        ProductFactory(slug='san-pham-a')
        with self.assertRaises(IntegrityError):
            ProductFactory(slug='san-pham-a')
```

---

## 2. Test Services

Test business logic — đây là phần quan trọng nhất cần coverage cao.

### Nguyên Tắc Test Service

- **Mỗi method một happy path test** — test khi mọi thứ đúng
- **Mỗi method một error case test** — test khi điều kiện không thỏa mãn
- **Mock external side effects** — email, SMS, payment gateway
- **Dùng `TestCase`** để DB tự rollback — không cần cleanup thủ công

```python
# orders/tests/test_services.py

from django.test import TestCase
from unittest.mock import patch, MagicMock
from .factories import OrderFactory, ProductFactory, UserFactory
from ..services.order_service import OrderService
from ..exceptions import (
    OrderNotFoundException,
    InsufficientStockError,
    InvalidOrderStatusTransitionError,
)
from ..constants import OrderStatus


class OrderServiceCreateTest(TestCase):
    """Test OrderService.create() — tạo đơn hàng mới."""

    def setUp(self):
        """Chuẩn bị dữ liệu dùng chung cho nhóm test này."""
        self.user = UserFactory()
        self.product = ProductFactory(price=100_000, stock=10)

    @patch('orders.services.order_service.NotificationService.send_order_confirmation')
    def test_create_order_returns_order_with_correct_total(self, mock_notify):
        """Tạo đơn hàng thành công, tổng tiền được tính đúng."""
        data = {
            'items': [{'product_id': self.product.id, 'quantity': 2}],
            'payment_method': 'cod',
        }

        order = OrderService.create(self.user, data)

        self.assertEqual(order.total, 200_000)  # 2 × 100,000
        self.assertEqual(order.status, OrderStatus.PENDING)
        self.assertEqual(order.user, self.user)

    @patch('orders.services.order_service.NotificationService.send_order_confirmation')
    def test_create_order_deducts_product_stock(self, mock_notify):
        """Khi tạo đơn, tồn kho sản phẩm phải bị trừ đúng số lượng."""
        initial_stock = self.product.stock
        data = {
            'items': [{'product_id': self.product.id, 'quantity': 3}],
            'payment_method': 'cod',
        }

        OrderService.create(self.user, data)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock - 3)

    @patch('orders.services.order_service.NotificationService.send_order_confirmation')
    def test_create_order_sends_confirmation_email(self, mock_notify):
        """Email xác nhận phải được gửi sau khi tạo đơn thành công."""
        data = {
            'items': [{'product_id': self.product.id, 'quantity': 1}],
            'payment_method': 'cod',
        }

        OrderService.create(self.user, data)

        # Kiểm tra email đã được gọi đúng 1 lần
        mock_notify.assert_called_once()

    def test_create_order_with_insufficient_stock_raises_error(self):
        """Tạo đơn khi tồn kho không đủ phải raise InsufficientStockError."""
        product = ProductFactory(stock=2)
        data = {
            'items': [{'product_id': product.id, 'quantity': 5}],  # cần 5, chỉ có 2
            'payment_method': 'cod',
        }

        with self.assertRaises(InsufficientStockError):
            OrderService.create(self.user, data)

    def test_create_order_with_insufficient_stock_does_not_change_stock(self):
        """Khi raise lỗi, tồn kho phải được rollback — không thay đổi."""
        product = ProductFactory(stock=2)
        data = {
            'items': [{'product_id': product.id, 'quantity': 5}],
            'payment_method': 'cod',
        }

        try:
            OrderService.create(self.user, data)
        except InsufficientStockError:
            pass

        product.refresh_from_db()
        self.assertEqual(product.stock, 2)  # không thay đổi


class OrderServiceCancelTest(TestCase):
    """Test OrderService.cancel() — hủy đơn hàng."""

    def test_cancel_pending_order_changes_status_to_cancelled(self):
        """Hủy đơn đang pending phải đổi status thành cancelled."""
        order = OrderFactory(status=OrderStatus.PENDING)

        OrderService.cancel(order)

        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.CANCELLED)

    def test_cancel_pending_order_restores_stock(self):
        """Hủy đơn phải hoàn lại tồn kho cho các sản phẩm trong đơn."""
        product = ProductFactory(stock=5)
        order = OrderFactory(status=OrderStatus.PENDING)
        # Giả sử order có 3 sản phẩm đã được đặt
        order.items.create(product=product, quantity=3, unit_price=product.price)

        OrderService.cancel(order)

        product.refresh_from_db()
        self.assertEqual(product.stock, 8)  # 5 + 3 hoàn lại

    def test_cancel_delivered_order_raises_error(self):
        """Không thể hủy đơn đã giao — phải raise InvalidOrderStatusTransitionError."""
        order = OrderFactory(status=OrderStatus.DELIVERED)

        with self.assertRaises(InvalidOrderStatusTransitionError):
            OrderService.cancel(order)

    def test_cancel_already_cancelled_order_raises_error(self):
        """Không thể hủy đơn đã bị hủy rồi."""
        order = OrderFactory(status=OrderStatus.CANCELLED)

        with self.assertRaises(InvalidOrderStatusTransitionError):
            OrderService.cancel(order)


class OrderPricingServiceTest(TestCase):
    """Test tính giá đơn hàng."""

    def setUp(self):
        self.user = UserFactory(membership_tier='gold')

    def test_gold_user_gets_10_percent_discount(self):
        """Thành viên Gold được giảm 10%."""
        discount = OrderPricingService.calculate_discount(1_000_000, self.user)
        self.assertEqual(discount, 100_000)

    def test_order_above_threshold_has_free_shipping(self):
        """Đơn hàng trên 500,000 VNĐ được miễn phí vận chuyển."""
        from ..constants import PaymentConfig
        shipping = OrderPricingService.calculate_shipping(600_000)
        self.assertEqual(shipping, 0)

    def test_order_below_threshold_has_shipping_fee(self):
        """Đơn hàng dưới 500,000 VNĐ phải trả phí ship."""
        from ..constants import PaymentConfig
        shipping = OrderPricingService.calculate_shipping(300_000)
        self.assertEqual(shipping, PaymentConfig.DEFAULT_SHIPPING_FEE)
```

---

## 3. Test Selectors

Test queries trả đúng dữ liệu, đúng bộ lọc.

```python
# orders/tests/test_selectors.py

from django.test import TestCase
from .factories import OrderFactory, UserFactory
from ..selectors.order_selector import OrderSelector
from ..constants import OrderStatus


class OrderSelectorTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()

    def test_get_orders_for_user_returns_only_that_users_orders(self):
        """Selector chỉ trả đơn hàng của đúng user được yêu cầu."""
        my_order = OrderFactory(user=self.user)
        other_order = OrderFactory(user=self.other_user)

        result = OrderSelector.get_orders_for_user(self.user)

        self.assertIn(my_order, result)
        self.assertNotIn(other_order, result)

    def test_get_orders_for_user_excludes_soft_deleted(self):
        """Selector không trả các đơn đã bị soft delete."""
        active_order = OrderFactory(user=self.user, is_active=True)
        deleted_order = OrderFactory(user=self.user, is_active=False)

        result = OrderSelector.get_orders_for_user(self.user)

        self.assertIn(active_order, result)
        self.assertNotIn(deleted_order, result)

    def test_get_orders_filter_by_status(self):
        """Lọc đơn hàng theo status."""
        pending = OrderFactory(user=self.user, status=OrderStatus.PENDING)
        delivered = OrderFactory(user=self.user, status=OrderStatus.DELIVERED)

        result = OrderSelector.get_orders_for_user(self.user, status=OrderStatus.PENDING)

        self.assertIn(pending, result)
        self.assertNotIn(delivered, result)

    def test_get_orders_ordered_by_newest_first(self):
        """Danh sách đơn phải sắp xếp mới nhất lên đầu."""
        from django.utils import timezone
        import datetime

        old_order = OrderFactory(user=self.user)
        old_order.created_at = timezone.now() - datetime.timedelta(days=5)
        old_order.save()

        new_order = OrderFactory(user=self.user)

        result = list(OrderSelector.get_orders_for_user(self.user))

        self.assertEqual(result[0], new_order)
        self.assertEqual(result[1], old_order)

    def test_selector_does_not_cause_n_plus_1_queries(self):
        """Selector phải dùng prefetch — không gây N+1 query."""
        # Tạo 5 orders với items
        for _ in range(5):
            order = OrderFactory(user=self.user)

        # Đếm số queries khi lấy danh sách
        from django.test.utils import CaptureQueriesContext
        from django.db import connection

        with CaptureQueriesContext(connection) as ctx:
            orders = list(OrderSelector.get_orders_for_user(self.user))
            # Truy cập items để trigger prefetch
            for order in orders:
                list(order.items.all())

        # Với prefetch_related, số queries phải cố định (không tăng theo số orders)
        self.assertLessEqual(len(ctx.captured_queries), 3)
```
