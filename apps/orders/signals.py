from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderItem


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
