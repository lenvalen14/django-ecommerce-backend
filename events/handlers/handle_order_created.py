import logging
from django.conf import settings
from events.producers.order_producer import send_kafka_event

logger = logging.getLogger(__name__)


def publish_order_created_event(order):
    logger.info(f"Preparing to send ORDER_CREATED for order_id={order.id}")

    event = {
        "event_type": "ORDER_CREATED",
        "order_id": order.id,
        "user_id": order.user.id,
        "email": order.user.email,
        "items": [
            {"product_id": item.product.id, "quantity": item.quantity}
            for item in order.order_items.all()
        ],
    }

    logger.debug(f"Event payload: {event}")

    send_kafka_event(settings.ORDER_TOPIC, event)

    logger.info(f"Sent ORDER_CREATED event for order_id={order.id}")
