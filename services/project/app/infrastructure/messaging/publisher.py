import json
import logging

try:
    import aio_pika
except ModuleNotFoundError:  # тесты могут работать без установленного клиента RabbitMQ
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
            log.warning("aio-pika is not installed; RabbitMQ publishing is disabled in this environment")
            return
        self.connection = await aio_pika.connect_robust(settings.rabbitmq_url, timeout=5)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(settings.rabbitmq_exchange, aio_pika.ExchangeType.TOPIC,
                                                            durable=True)

    async def publish(self, event: dict):
        if aio_pika is None:
            log.info("event published (local fallback)", extra={"event_type": event["event_type"]})
            return
        try:
            if self.exchange is None or self.connection.is_closed:
                await self.connect()
            if self.exchange is None:
                return
            await self.exchange.publish(
                aio_pika.Message(body=json.dumps(event).encode(), content_type="application/json",
                                 delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                routing_key=event["event_type"])
        except Exception:
            # Недоступность RabbitMQ не должна валить запрос — изменения в БД уже применены.
            log.warning("failed to publish event; continuing without it", extra={"event_type": event["event_type"]})

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()


publisher = RabbitPublisher()
