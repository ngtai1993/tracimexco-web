# Django App — Code Templates Chuẩn

## models/`<model_name>`.py

```python
from django.db import models
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    name = models.CharField(_('name'), max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(_('description'), blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
        ordering = ['-created_at']

    def __str__(self):
        return self.name
```

## models/`__init__.py`

```python
# Luôn export models ở đây để Django migration phát hiện được
from .product import Product

__all__ = ['Product']
```

---

## services/`<feature>_service.py`

```python
from django.db import transaction
from ..models import Product


class ProductService:
    @staticmethod
    def get_active_list():
        return Product.objects.filter(is_active=True).order_by('-created_at')

    @staticmethod
    def get_by_id(product_id: int) -> Product:
        return Product.objects.get(pk=product_id, is_active=True)

    @staticmethod
    @transaction.atomic
    def create(data: dict) -> Product:
        product = Product(**data)
        product.full_clean()
        product.save()
        return product

    @staticmethod
    @transaction.atomic
    def update(product: Product, data: dict) -> Product:
        for field, value in data.items():
            setattr(product, field, value)
        product.full_clean()
        product.save()
        return product

    @staticmethod
    def soft_delete(product: Product) -> None:
        """Xóa mềm sản phẩm — đánh dấu inactive, KHÔNG xóa khỏi DB."""
        product.is_active = False
        product.save(update_fields=['is_active'])
```

---

## views/`<feature>_views.py` — Class-Based View

```python
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from ..services.product_service import ProductService


class ProductListView(LoginRequiredMixin, ListView):
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return ProductService.get_active_list()


class ProductDetailView(LoginRequiredMixin, DetailView):
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_object(self):
        return ProductService.get_by_id(self.kwargs['pk'])
```

## views/`<feature>_views.py` — DRF API View

```python
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..services.product_service import ProductService
from ..serializers.product_serializer import ProductSerializer


class ProductListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = ProductService.get_active_list()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = ProductService.create(serializer.validated_data)
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
```

## views/`__init__.py`

```python
from .product_views import ProductListView, ProductDetailView

__all__ = ['ProductListView', 'ProductDetailView']
```

---

## selectors/`<feature>_selector.py`

```python
from ..models import Product


class ProductSelector:
    @staticmethod
    def get_active_list(search: str = None):
        """Lấy danh sách sản phẩm đang bán, hỗ trợ tìm kiếm theo tên."""
        qs = Product.objects.filter(is_active=True).order_by('-created_at')
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    @staticmethod
    def get_by_id(product_id: int) -> Product:
        """Lấy sản phẩm đang active theo ID."""
        return Product.objects.get(pk=product_id, is_active=True)

    @staticmethod
    def get_list_with_category():
        """Lấy danh sách sản phẩm kèm thông tin danh mục — dùng select_related tránh N+1."""
        return (
            Product.objects
            .filter(is_active=True)
            .select_related('category')
            .prefetch_related('tags')
            .order_by('-created_at')
        )
```

## selectors/`__init__.py`

```python
from .product_selector import ProductSelector

__all__ = ['ProductSelector']
```

---

## exceptions.py

```python
# <app_name>/exceptions.py


class ProductNotFoundException(Exception):
    """Không tìm thấy sản phẩm với ID đã cho."""
    pass


class ProductAlreadyInactiveError(Exception):
    """Sản phẩm đã bị vô hiệu hóa trước đó."""
    pass


class InsufficientStockError(Exception):
    """Tồn kho không đủ để thực hiện thao tác."""
    def __init__(self, product_name: str, available: int, required: int):
        super().__init__(
            f'Sản phẩm "{product_name}" không đủ tồn kho '
            f'(còn {available}, cần {required})'
        )
```

---

## constants.py

```python
# <app_name>/constants.py


class ProductStatus:
    """Trạng thái sản phẩm trong hệ thống."""
    DRAFT = 'draft'           # Bản nháp, chưa hiển thị
    ACTIVE = 'active'         # Đang bán
    OUT_OF_STOCK = 'out_of_stock'  # Hết hàng
    DISCONTINUED = 'discontinued'  # Ngừng kinh doanh

    CHOICES = [
        (DRAFT, 'Bản nháp'),
        (ACTIVE, 'Đang bán'),
        (OUT_OF_STOCK, 'Hết hàng'),
        (DISCONTINUED, 'Ngừng kinh doanh'),
    ]

    # Trạng thái hiển thị cho khách hàng
    VISIBLE_STATUSES = [ACTIVE, OUT_OF_STOCK]


class ProductConfig:
    """Cấu hình giới hạn cho sản phẩm."""
    MAX_IMAGES_PER_PRODUCT = 10   # Tối đa 10 ảnh mỗi sản phẩm
    MAX_NAME_LENGTH = 255         # Độ dài tên tối đa
    LOW_STOCK_THRESHOLD = 5       # Cảnh báo tồn kho thấp khi còn <= 5
```

---

## serializers/`<model>_serializer.py` — DRF

```python
from rest_framework import serializers
from ..models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
```

---

## admin.py

```python
from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
```

---

## tests/`test_services.py`

```python
from django.test import TestCase
from ..models import Product
from ..services.product_service import ProductService


class ProductServiceTestCase(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
        )

    def test_get_active_list_returns_active_only(self):
        products = ProductService.get_active_list()
        self.assertIn(self.product, products)

    def test_create_product(self):
        data = {'name': 'New Product', 'slug': 'new-product'}
        product = ProductService.create(data)
        self.assertEqual(product.name, 'New Product')

    def test_soft_delete(self):
        ProductService.soft_delete(self.product)
        self.product.refresh_from_db()
        self.assertFalse(self.product.is_active)
```
