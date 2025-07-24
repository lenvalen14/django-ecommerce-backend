from config import settings
from events.producers.order_producer import send_kafka_event


def publish_order_delivered_event(order):
    event = {
        "event_type": "ORDER_DELIVERED",
        "order_id": order.id,
        "user_id": order.user.id,
        "email": order.user.email,
    }
    send_kafka_event(settings.ORDER_TOPIC, event)