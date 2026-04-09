# API Tests — DRF Endpoints

## Setup: APIClient & Helpers

```python
# orders/tests/test_views.py

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch
from .factories import OrderFactory, ProductFactory, UserFactory
from ..constants import OrderStatus


class BaseAPITestCase(APITestCase):
    """Base class dùng chung cho tất cả API test — tự xử lý login."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()

    def authenticate(self, user=None):
        """Đăng nhập user (mặc định là self.user)."""
        target = user or self.user
        self.client.force_authenticate(user=target)

    def get(self, url_name, **kwargs):
        return self.client.get(reverse(url_name, **kwargs))

    def post(self, url_name, data=None, **kwargs):
        return self.client.post(reverse(url_name, **kwargs), data, format='json')

    def patch(self, url_name, data=None, **kwargs):
        return self.client.patch(reverse(url_name, **kwargs), data, format='json')
```

---

## 1. Template Test Chuẩn Cho Mỗi Endpoint

Mỗi endpoint cần test theo đúng thứ tự:

```
1. Happy path (thành công)
2. Chưa xác thực → 401
3. Input sai / thiếu → 400
4. Không có quyền → 403
5. Resource không tồn tại → 404
6. Conflict / trạng thái không hợp lệ → 409
```

---

## 2. Test List Endpoint (GET danh sách)

```python
class OrderListAPITest(BaseAPITestCase):
    """Test GET /api/orders/ — lấy danh sách đơn hàng."""

    def test_authenticated_user_gets_own_orders(self):
        """User đã đăng nhập lấy được danh sách đơn của mình."""
        self.authenticate()
        my_order = OrderFactory(user=self.user)
        other_order = OrderFactory()  # đơn của user khác

        response = self.get('orders:list')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order_ids = [o['id'] for o in response.data['results']]
        self.assertIn(my_order.id, order_ids)
        self.assertNotIn(other_order.id, order_ids)

    def test_unauthenticated_request_returns_401(self):
        """Chưa đăng nhập phải trả 401."""
        response = self.get('orders:list')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_by_status_returns_only_matching_orders(self):
        """Lọc theo status chỉ trả đúng các đơn có status đó."""
        self.authenticate()
        pending = OrderFactory(user=self.user, status=OrderStatus.PENDING)
        delivered = OrderFactory(user=self.user, status=OrderStatus.DELIVERED)

        response = self.client.get(
            reverse('orders:list'),
            {'status': OrderStatus.PENDING}
        )

        order_ids = [o['id'] for o in response.data['results']]
        self.assertIn(pending.id, order_ids)
        self.assertNotIn(delivered.id, order_ids)

    def test_response_has_pagination_fields(self):
        """Response phải có đủ fields phân trang: count, next, previous, results."""
        self.authenticate()

        response = self.get('orders:list')

        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
```

---

## 3. Test Create Endpoint (POST tạo mới)

```python
class OrderCreateAPITest(BaseAPITestCase):
    """Test POST /api/orders/ — tạo đơn hàng mới."""

    def setUp(self):
        super().setUp()
        self.product = ProductFactory(price=100_000, stock=10)
        self.valid_payload = {
            'items': [{'product_id': self.product.id, 'quantity': 2}],
            'payment_method': 'cod',
        }

    @patch('orders.services.order_service.NotificationService.send_order_confirmation')
    def test_create_order_returns_201_with_order_data(self, mock_notify):
        """Tạo đơn thành công phải trả 201 kèm dữ liệu đơn hàng."""
        self.authenticate()

        response = self.post('orders:list', self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['status'], OrderStatus.PENDING)

    @patch('orders.services.order_service.NotificationService.send_order_confirmation')
    def test_create_order_deducts_stock(self, mock_notify):
        """Tạo đơn phải trừ tồn kho sản phẩm."""
        self.authenticate()
        initial_stock = self.product.stock

        self.post('orders:list', self.valid_payload)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock - 2)

    def test_unauthenticated_cannot_create_order(self):
        """Chưa đăng nhập không được tạo đơn."""
        response = self.post('orders:list', self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_items_field_returns_400(self):
        """Thiếu field items bắt buộc phải trả 400."""
        self.authenticate()
        payload = {'payment_method': 'cod'}  # thiếu items

        response = self.post('orders:list', payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('items', response.data)

    def test_invalid_payment_method_returns_400(self):
        """payment_method không hợp lệ phải trả 400."""
        self.authenticate()
        payload = {**self.valid_payload, 'payment_method': 'bitcoin'}

        response = self.post('orders:list', payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_insufficient_stock_returns_400(self):
        """Đặt nhiều hơn tồn kho phải trả 400."""
        self.authenticate()
        payload = {
            'items': [{'product_id': self.product.id, 'quantity': 999}],
            'payment_method': 'cod',
        }

        response = self.post('orders:list', payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_items_list_returns_400(self):
        """Danh sách items rỗng phải trả 400."""
        self.authenticate()
        payload = {**self.valid_payload, 'items': []}

        response = self.post('orders:list', payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
```

---

## 4. Test Detail Endpoint (GET, PATCH, DELETE một object)

```python
class OrderDetailAPITest(BaseAPITestCase):
    """Test GET/PATCH /api/orders/{id}/ — chi tiết đơn hàng."""

    def setUp(self):
        super().setUp()
        self.order = OrderFactory(user=self.user)
        self.other_order = OrderFactory()  # thuộc user khác

    def test_owner_can_view_own_order(self):
        """Chủ đơn hàng xem được chi tiết đơn của mình."""
        self.authenticate()

        response = self.client.get(
            reverse('orders:detail', kwargs={'pk': self.order.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order.id)

    def test_unauthenticated_cannot_view_order(self):
        """Chưa đăng nhập không xem được."""
        response = self.client.get(
            reverse('orders:detail', kwargs={'pk': self.order.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_cannot_view_other_users_order(self):
        """User không được xem đơn hàng của người khác — phải trả 403 hoặc 404."""
        self.authenticate()

        response = self.client.get(
            reverse('orders:detail', kwargs={'pk': self.other_order.id})
        )

        self.assertIn(response.status_code, [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ])

    def test_nonexistent_order_returns_404(self):
        """ID không tồn tại phải trả 404."""
        self.authenticate()

        response = self.client.get(
            reverse('orders:detail', kwargs={'pk': 99999})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
```

---

## 5. Test Action Endpoint (PATCH cancel, approve...)

```python
class OrderCancelAPITest(BaseAPITestCase):
    """Test PATCH /api/orders/{id}/cancel/ — hủy đơn hàng."""

    def test_owner_can_cancel_pending_order(self):
        """Chủ đơn hủy được khi đơn đang pending."""
        self.authenticate()
        order = OrderFactory(user=self.user, status=OrderStatus.PENDING)

        response = self.client.patch(
            reverse('orders:cancel', kwargs={'pk': order.id}),
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.CANCELLED)

    def test_cannot_cancel_delivered_order_returns_409(self):
        """Hủy đơn đã giao phải trả 409 Conflict."""
        self.authenticate()
        order = OrderFactory(user=self.user, status=OrderStatus.DELIVERED)

        response = self.client.patch(
            reverse('orders:cancel', kwargs={'pk': order.id}),
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_cancel_order_by_non_owner_returns_403(self):
        """User khác không thể hủy đơn của người khác."""
        other_user = UserFactory()
        self.authenticate(other_user)
        order = OrderFactory(user=self.user, status=OrderStatus.PENDING)

        response = self.client.patch(
            reverse('orders:cancel', kwargs={'pk': order.id}),
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
```

---

## 6. Test Admin-Only Endpoints

```python
class OrderAdminAPITest(BaseAPITestCase):
    """Test các endpoint chỉ dành cho Admin."""

    def setUp(self):
        super().setUp()
        self.admin = UserFactory(is_staff=True)
        self.order = OrderFactory()

    def test_admin_can_update_order_status(self):
        """Admin cập nhật được trạng thái đơn hàng."""
        self.authenticate(self.admin)

        response = self.client.patch(
            reverse('orders:admin-status', kwargs={'pk': self.order.id}),
            {'status': OrderStatus.PROCESSING},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_cannot_update_order_status(self):
        """User thường không được cập nhật status — phải trả 403."""
        self.authenticate()  # user thường

        response = self.client.patch(
            reverse('orders:admin-status', kwargs={'pk': self.order.id}),
            {'status': OrderStatus.PROCESSING},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
```

---

## 7. Kiểm Tra Response Schema

```python
def test_order_response_has_required_fields(self):
    """Response phải có đủ các fields đã định nghĩa trong serializer."""
    self.authenticate()
    order = OrderFactory(user=self.user)

    response = self.client.get(
        reverse('orders:detail', kwargs={'pk': order.id})
    )

    # Kiểm tra tất cả fields bắt buộc có trong response
    required_fields = ['id', 'status', 'total', 'created_at', 'items']
    for field in required_fields:
        self.assertIn(field, response.data, f'Thiếu field "{field}" trong response')

def test_order_list_uses_summary_serializer(self):
    """Danh sách đơn không được trả items chi tiết — giữ response gọn."""
    self.authenticate()
    OrderFactory(user=self.user)

    response = self.get('orders:list')

    # Danh sách chỉ có fields tóm tắt, không có 'items' chi tiết
    first_order = response.data['results'][0]
    self.assertNotIn('items', first_order)
```
