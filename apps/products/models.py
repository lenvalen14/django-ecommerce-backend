"""
Models for product and category management.
"""

from cloudinary.models import CloudinaryField
from django.db import models
from django.db.models import F
from django.utils.html import format_html
from rest_framework.exceptions import ValidationError


class Category(models.Model):
    """
    Danh mục sản phẩm.
    """
    category_name = models.CharField(max_length=100)

    @property
    def product_count(self):
        """
        Đếm tổng số sản phẩm thuộc về danh mục này.
        """
        return self.products.count()

    def __str__(self) -> str:
        return str(self.category_name)


class Product(models.Model):
    """
    Sản phẩm được bán trong hệ thống.
    """
    product_name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products'
    )
    stock_quantity = models.PositiveIntegerField()
    image = CloudinaryField('image')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def is_available(self):
        return self.stock_quantity > 0

    def image_tag(self):
        if self.image:
            return format_html('<img src="{}" width="50"/>', self.image.url)
        return "No Image"

    image_tag.short_description = "Thumbnail"

    def decrease_stock(self, quantity: int) -> None:
        """
        Giảm số lượng tồn kho một cách an toàn để tránh race condition.
        Hàm này sẽ được gọi khi một đơn hàng được tạo.
        """
        if quantity <= 0:
            raise ValidationError("Số lượng đặt hàng phải là số dương.")

        rows_updated = Product.objects.filter(
            pk=self.pk,
            stock_quantity__gte=quantity
        ).update(
            stock_quantity=F('stock_quantity') - quantity
        )

        # Nếu không có dòng nào được cập nhật, nghĩa là không đủ hàng
        if rows_updated == 0:
            self.refresh_from_db(fields=['stock_quantity'])
            raise ValidationError(
                f"Không đủ hàng tồn kho. Chỉ còn lại {self.stock_quantity} sản phẩm."
            )

        # Cập nhật lại instance hiện tại với giá trị mới từ DB
        self.refresh_from_db(fields=['stock_quantity'])

    def __str__(self) -> str:
        return str(self.product_name)
