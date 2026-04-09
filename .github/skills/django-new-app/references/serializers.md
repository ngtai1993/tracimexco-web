# Django App — Nguyên Tắc Viết Serializer & Áp Dụng Vào Views

## Vai Trò Của Serializer

Serializer chỉ có 2 nhiệm vụ:
1. **Validate input** — kiểm tra dữ liệu đầu vào từ request
2. **Serialize output** — chuyển model/queryset sang JSON trả về client

```
Request data → Serializer (validate) → Service (business logic) → Serializer (output) → Response
```

**Serializer KHÔNG được:**
- Chứa business logic (tính giá, gửi email, trừ tồn kho...)
- Gọi trực tiếp vào DB để tạo/cập nhật dữ liệu (trừ khi rất đơn giản)
- Biết về `request.user` hay bất kỳ HTTP context nào

---

## 1. Tách Read Serializer và Write Serializer

Dùng **2 serializer riêng** cho đọc và ghi — tránh một serializer cố làm cả hai:

```python
# orders/serializers/order_serializer.py

from rest_framework import serializers
from ..models import Order, OrderItem
from ..constants import OrderStatus


# --- WRITE SERIALIZER: nhận input từ client khi tạo/cập nhật ---

class OrderItemInputSerializer(serializers.Serializer):
    """Validate từng item trong đơn hàng khi tạo mới."""
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1, max_value=100)


class OrderCreateSerializer(serializers.Serializer):
    """Validate input khi tạo đơn hàng mới."""
    items = OrderItemInputSerializer(many=True, min_length=1)
    shipping_address_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=['cod', 'vnpay', 'momo'])
    note = serializers.CharField(max_length=500, required=False, allow_blank=True)
    voucher_code = serializers.CharField(max_length=50, required=False)


# --- READ SERIALIZER: định nghĩa output trả về client ---

class OrderItemOutputSerializer(serializers.ModelSerializer):
    """Serialize từng item trong đơn hàng để trả về client."""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'product_name', 'product_sku', 'quantity', 'unit_price']


class OrderOutputSerializer(serializers.ModelSerializer):
    """Serialize đơn hàng để trả về client — dữ liệu đầy đủ."""
    items = OrderItemOutputSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    customer_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'status_display', 'customer_name',
            'subtotal', 'shipping_fee', 'discount', 'total',
            'note', 'created_at', 'items',
        ]
        read_only_fields = fields  # Output serializer: tất cả đều read_only


class OrderListOutputSerializer(serializers.ModelSerializer):
    """Serialize đơn hàng dạng tóm tắt cho danh sách — ít field hơn để nhanh hơn."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'status_display', 'total', 'created_at']
        read_only_fields = fields
```

---

## 2. Validation Trong Write Serializer

### Validate Từng Field

```python
class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemInputSerializer(many=True, min_length=1)
    payment_method = serializers.ChoiceField(choices=['cod', 'vnpay', 'momo'])
    voucher_code = serializers.CharField(max_length=50, required=False)

    def validate_voucher_code(self, value):
        """Kiểm tra voucher tồn tại và còn hiệu lực."""
        if not value:
            return value
        # Chỉ validate sự tồn tại — KHÔNG áp dụng discount ở đây
        # Logic áp dụng discount thuộc về service
        from vouchers.selectors.voucher_selector import VoucherSelector
        if not VoucherSelector.is_valid_code(value):
            raise serializers.ValidationError('Mã giảm giá không hợp lệ hoặc đã hết hạn.')
        return value
```

### Validate Nhiều Field Cùng Lúc (Cross-field Validation)

```python
class DateRangeSerializer(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()

    def validate(self, attrs):
        """Kiểm tra từ ngày phải nhỏ hơn đến ngày."""
        if attrs['from_date'] > attrs['to_date']:
            raise serializers.ValidationError({
                'to_date': 'Ngày kết thúc phải sau ngày bắt đầu.'
            })
        return attrs
```

### KHÔNG Validate Business Logic Trong Serializer

```python
# ❌ KHÔNG làm — business logic trong serializer
class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemInputSerializer(many=True)

    def validate_items(self, items):
        for item in items:
            product = Product.objects.get(pk=item['product_id'])
            if product.stock < item['quantity']:
                raise serializers.ValidationError('Không đủ tồn kho')  # ← business logic!
        return items

# ✅ NÊN làm — serializer chỉ validate format, service xử lý business
class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemInputSerializer(many=True)
    # Không gọi DB trong serializer — để service làm
```

---

## 3. Áp Dụng Serializer Trong Views

### Pattern Chuẩn: Input → Service → Output

```python
# orders/views/order_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ..serializers.order_serializer import (
    OrderCreateSerializer,    # write — validate input
    OrderOutputSerializer,    # read — serialize output chi tiết
    OrderListOutputSerializer, # read — serialize output danh sách
)
from ..services.order_service import OrderService
from ..selectors.order_selector import OrderSelector


class OrderListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Lấy danh sách đơn hàng của user hiện tại."""
        # 1. Lấy dữ liệu qua selector (không cần serializer input)
        orders = OrderSelector.get_orders_for_user(request.user)

        # 2. Serialize output — dùng list serializer (ít field hơn)
        serializer = OrderListOutputSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Tạo đơn hàng mới."""
        # 1. Validate input bằng write serializer
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Tự trả 400 nếu invalid

        # 2. Gọi service với validated data — KHÔNG gọi serializer.save()
        order = OrderService.create(
            user=request.user,
            data=serializer.validated_data,  # đã được validate sạch
        )

        # 3. Serialize output bằng read serializer
        output = OrderOutputSerializer(order)
        return Response(output.data, status=status.HTTP_201_CREATED)


class OrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Lấy chi tiết một đơn hàng."""
        from ..exceptions import OrderNotFoundException
        try:
            order = OrderSelector.get_order_detail(pk, request.user)
        except OrderNotFoundException as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderOutputSerializer(order)
        return Response(serializer.data)

    def patch(self, request, pk):
        """Cập nhật một phần đơn hàng (vd: ghi chú)."""
        from ..serializers.order_serializer import OrderUpdateSerializer
        from ..exceptions import OrderNotFoundException

        serializer = OrderUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = OrderService.update(pk, request.user, serializer.validated_data)
        except OrderNotFoundException as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response(OrderOutputSerializer(order).data)
```

---

## 4. Nested Serializer (Serializer Lồng Nhau)

```python
# products/serializers/product_serializer.py

class CategoryOutputSerializer(serializers.ModelSerializer):
    """Serialize danh mục — dùng làm nested trong product."""
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = fields


class ProductOutputSerializer(serializers.ModelSerializer):
    """Serialize sản phẩm kèm danh mục lồng vào."""
    # Nested serializer — category là object đầy đủ, không chỉ là ID
    category = CategoryOutputSerializer(read_only=True)

    # SerializerMethodField — computed field tính toán từ model
    is_in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'category', 'is_in_stock', 'created_at']
        read_only_fields = fields

    def get_is_in_stock(self, obj) -> bool:
        """Tính toán xem sản phẩm có còn hàng không."""
        return obj.stock > 0
```

**Lưu ý quan trọng với nested serializer:** Đảm bảo query đã dùng `select_related` / `prefetch_related` trước khi serialize để tránh N+1:

```python
# selector phải prefetch trước
class ProductSelector:
    @staticmethod
    def get_active_list():
        """Lấy sản phẩm kèm category — tránh N+1 khi serialize nested."""
        return (
            Product.objects
            .filter(is_active=True)
            .select_related('category')   # bắt buộc nếu serialize lồng category
            .order_by('-created_at')
        )
```

---

## 5. `__init__.py` Trong `serializers/`

Export đầy đủ để import gọn hơn trong views:

```python
# serializers/__init__.py

from .order_serializer import (
    OrderCreateSerializer,
    OrderUpdateSerializer,
    OrderOutputSerializer,
    OrderListOutputSerializer,
)

__all__ = [
    'OrderCreateSerializer',
    'OrderUpdateSerializer',
    'OrderOutputSerializer',
    'OrderListOutputSerializer',
]
```

```python
# views dùng import gọn
from ..serializers import OrderCreateSerializer, OrderOutputSerializer
```

---

## 6. Checklist Serializer

Trước khi commit serializer mới, kiểm tra:

- [ ] Write serializer và Read serializer được tách riêng
- [ ] `read_only_fields` được khai báo đầy đủ trong output serializer
- [ ] Không có business logic (gọi DB để create/update) trong serializer
- [ ] `validate_<field>` chỉ validate format, không chứa business rule
- [ ] Nested serializer đi kèm với `select_related`/`prefetch_related` trong selector
- [ ] `__init__.py` export đầy đủ
- [ ] Views dùng `serializer.validated_data` rồi truyền vào service — không dùng `serializer.save()`
