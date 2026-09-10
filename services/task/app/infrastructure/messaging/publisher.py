import json
import logging
try:
    import aio_pika
except ModuleNotFoundError:
    aio_pika = None

from app.core.config import settings

log = logging.getLogger(__name__)


class RabbitPublisher:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None

    async def connect(self):
        if aio_pika is None:
            log.warning("aio-pika is not installed; RabbitMQ publishing is disabled")
            return
        if self.connection and not self.connection.is_closed:
            return
        self.connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(
            settings.rabbitmq_exchange, aio_pika.ExchangeType.TOPIC, durable=True
        )

    async def publish(self, event: dict):
        if aio_pika is None:
            log.info("RabbitMQ event skipped in local environment", extra={"event_type": event["event_type"]})
            return
        if not self.connection or self.connection.is_closed:
            await self.connect()
        await self.exchange.publish(
            aio_pika.Message(
                body=json.dumps(event).encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=event["event_type"],
        )

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
