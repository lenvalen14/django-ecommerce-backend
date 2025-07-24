from django.core.management.base import BaseCommand
from events.consumers.order_consumer import run_consumer

class Command(BaseCommand):
    help = 'Run Kafka consumer for order-events'

    def handle(self, *args, **options):
        run_consumer()
