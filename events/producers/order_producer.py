from confluent_kafka import Producer
import os
import django
import json
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings

logger = logging.getLogger(__name__)
producer = Producer({'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS})

def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

def send_kafka_event(topic, event):
    try:
        payload = json.dumps(event).encode("utf-8")
        producer.produce(topic=topic, value=payload, callback=delivery_report)
        producer.flush()
        logger.info(f"Produced event to Kafka topic '{topic}'")
    except Exception as e:
        logger.exception("Failed to send Kafka event")
        raise
