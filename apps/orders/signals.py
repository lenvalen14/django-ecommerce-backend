from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderItem, Order, OrderStatus


@receiver([post_save, post_delete], sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    order = instance.order
    if not order:
        return

    total = sum(
        item.unit_price * item.quantity
        for item in order.order_items.all()
    )
    order.total_price = total
    order.save(update_fields=["total_price"])

@receiver(post_save, sender=Order)
def restore_product_quantity_when_cancel(sender, instance, created, **kwargs):
    if not created and instance.status == OrderStatus.CANCELED:
        for item in instance.order_items.all():
            product = item.product
            product.stock_quantity += item.quantity
            product.save(update_fields=['stock_quantity'])
