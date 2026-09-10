from app.core.config import settings


class RabbitConnection:
    def __init__(self) -> None:
        self.connection = None
        self.channel = None

    async def connect(self) -> None:
        import aio_pika
        self.connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=10)

    async def setup(self):
        import aio_pika
        if not self.channel:
            raise RuntimeError("RabbitMQ is not connected")
        main_exchange = await self.channel.declare_exchange(settings.rabbitmq_exchange, aio_pika.ExchangeType.TOPIC, durable=True)
        dlx_exchange = await self.channel.declare_exchange(settings.rabbitmq_dlx_exchange, aio_pika.ExchangeType.DIRECT, durable=True)
        dlq = await self.channel.declare_queue(settings.rabbitmq_dlq, durable=True)
        await dlq.bind(dlx_exchange, routing_key=settings.rabbitmq_dlq)
        queue = await self.channel.declare_queue(
            settings.rabbitmq_queue,
            durable=True,
            arguments={
                "x-dead-letter-exchange": settings.rabbitmq_dlx_exchange,
                "x-dead-letter-routing-key": settings.rabbitmq_dlq,
            },
        )
        # Должно совпадать с event_type, который шлют producer'ы (например, "TaskAssigned").
        for key in ("TaskAssigned", "TaskStatusChanged", "TaskCompleted", "TaskDeadlineChanged",
                   "ProjectMemberAdded", "ProjectInvitationCreated"):
            await queue.bind(main_exchange, routing_key=key)
        return main_exchange, queue, dlx_exchange

    async def close(self) -> None:
        if self.connection:
            await self.connection.close()
