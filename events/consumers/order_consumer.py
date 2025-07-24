import os
import django
import logging
import json
from confluent_kafka import Consumer
from django.core.mail import send_mail
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)
logger.info("Kafka consumer started")

from apps.notifications.models import Notification
from apps.products.models import Product


def run_consumer():
    logger.info("🟢 Kafka consumer is starting...")

    consumer = Consumer({
        'bootstrap.servers': 'kafka:9092',
        'group.id': 'order-consumer-group',
        'auto.offset.reset': 'earliest'
    })

    consumer.subscribe(['order-events'])
    logger.info("Subscribed to topic: order-events")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logger.warning(f"Consumer error: {msg.error()}")
                continue

            try:
                data = json.loads(msg.value().decode('utf-8'))
                event_type = data.get("event_type")
                logger.info(f"Received event: {event_type} | Payload: {data}")

                if event_type == "ORDER_CREATED":
                    for item in data["items"]:
                        try:
                            product = Product.objects.get(id=item["product_id"])
                            product.stock_quantity -= item["quantity"]
                            product.save()
                            logger.info(f"Updated stock for product_id={product.id}")
                        except Product.DoesNotExist:
                            logger.warning(f"Product {item['product_id']} not found")

                    Notification.objects.create(
                        user_id=data["user_id"],
                        title="Đơn hàng đã được tạo",
                        message=f"Đơn hàng #{data['order_id']} của bạn đã được ghi nhận.",
                        type="order"
                    )
                    logger.info(f"Notification sent for user_id={data['user_id']}")

                    send_mail(
                        subject="Xác nhận đơn hàng",
                        message=f"Chúng tôi đã nhận đơn hàng #{data['order_id']}.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[data["email"]],
                    )
                    logger.info(f"Email sent to {data['email']}")

                elif event_type == "ORDER_DELIVERED":
                    Notification.objects.create(
                        user_id=data["user_id"],
                        title="Đơn hàng đã được giao",
                        message=f"Đơn hàng #{data['order_id']} đã được giao thành công.",
                        type="order"
                    )
                    logger.info(f"Notification for delivery sent to user {data['user_id']}")

                    send_mail(
                        subject="Đơn hàng đã giao thành công",
                        message=f"Đơn hàng #{data['order_id']} đã đến tay bạn.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[data["email"]],
                    )
                    logger.info(f"Delivery email sent to {data['email']}")
                elif event_type == "ORDER_CANCELED":
                    for item in data["items"]:
                        try:
                            product = Product.objects.get(id=item["product_id"])
                            product.stock_quantity += item["quantity"]
                            product.save()
                            logger.info(f" Restocked for product_id={product.id}")
                        except Product.DoesNotExist:
                            logger.warning(f"Product {item['product_id']} not found")

            except Exception as e:
                logger.exception("Error processing event")

    except KeyboardInterrupt:
        logger.info("Kafka consumer stopped by user.")
    finally:
        consumer.close()
        logger.info("Kafka consumer closed.")

if __name__ == "__main__":
    run_consumer()
