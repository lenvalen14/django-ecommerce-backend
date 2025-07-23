"""
Models for managing orders and order items in the e-commerce system.
"""
from itertools import product

from django.contrib.auth import get_user_model
from django.db import models

from apps.products.models import Product

User = get_user_model()


class OrderStatus(models.TextChoices):
    """
    Enum đại diện cho các trạng thái đơn hàng.
    """
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    PROCESSING = 'processing', 'Processing'
    SHIPPED = 'shipped', 'Shipped'
    DELIVERED = 'delivered', 'Delivered'
    CANCELED = 'canceled', 'Canceled'
    RETURNED = 'returned', 'Returned'


class Order(models.Model):
    """
    Đại diện cho một đơn hàng.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def update_total_price(self) -> None:
        """
        Tính lại tổng giá đơn hàng dựa trên các mục trong đơn.
        """
        total = sum(
            item.unit_price * item.quantity
            for item in self.order_items.all()
        )
        self.total_price = total
        self.save(update_fields=["total_price"])

    def __str__(self) -> str:
        return f"Order #{self.pk} by {self.user}"


class OrderItem(models.Model):
    """
    Đại diện cho một sản phẩm trong đơn hàng.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.product} x{self.quantity}"
