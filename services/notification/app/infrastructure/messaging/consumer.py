import json
import logging

from app.application.services.notification_consumer import process_event
from app.core.config import settings

log = logging.getLogger(__name__)


def _retry_count(message) -> int:
    try:
        return int(message.headers.get("x-retry-count", 0))
    except (TypeError, ValueError):
        return 0


async def start_consumer(queue, dlx_exchange) -> None:
    import aio_pika

    async def on_message(message) -> None:
        try:
            envelope = json.loads(message.body.decode("utf-8"))
            await process_event(envelope, settings.consumer_name)
            await message.ack()
        except Exception:
            retries = _retry_count(message) + 1
            log.exception("notification_event_processing_failed retry=%s", retries)
            try:
                target_exchange = message.channel.default_exchange if retries < settings.rabbitmq_max_retries else dlx_exchange
                target_key = settings.rabbitmq_queue if retries < settings.rabbitmq_max_retries else settings.rabbitmq_dlq
                await target_exchange.publish(
                    aio_pika.Message(
                        body=message.body,
                        content_type="application/json",
                        headers={**message.headers, "x-retry-count": retries},
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    ),
                    routing_key=target_key,
                )
                await message.ack()
            except Exception:
                log.exception("notification_event_requeue_or_dlq_failed")
                await message.nack(requeue=False)

    await queue.consume(on_message)
