import logging

from config import settings
from events.producers.order_producer import send_kafka_event
logger = logging.getLogger(__name__)
def publish_order_canceled_event(order):
    event = {
        "event_type": "ORDER_CANCELED",
        "order_id": order.id,
        "user_id": order.user.id,
        "email": order.user.email,
        "items": [
            {"product_id": item.product.id, "quantity": item.quantity}
            for item in order.order_items.all()
        ],
    }
    logger.info(f"Sending ORDER_CANCELED event for order_id={order.id}")
    send_kafka_event(settings.ORDER_TOPIC, event)
