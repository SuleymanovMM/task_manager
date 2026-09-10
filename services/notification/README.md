# Notification Service

Простой Notification Service для TaskManager.

## Ответственность

Сервис только читает события из RabbitMQ и создаёт уведомления в собственной `notification_db`. Он не изменяет Task, Project или User и не делает HTTP-запросов к этим сервисам.

## Запуск

```bash
cp .env.example .env
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8003
```

Тестовые инструменты (`pytest`, `pytest-asyncio`) не входят в `requirements.txt` — ставятся в venv отдельно, только для запуска тестов.

Для Docker сервис рассчитан на существующие PostgreSQL и RabbitMQ из общего TaskManager.

## JWT

Используется публичный RS256-ключ Identity Service:

```text
secrets/public.pem
```

Приватный ключ здесь не нужен и не должен находиться в сервисе.

## RabbitMQ

Main exchange: `taskflow.events`

Main queue: `notification-service.notifications`

DLQ exchange: `taskflow.events.dlq`

DLQ queue: `notification-service.notifications.dlq`

После трёх неудачных обработок событие отправляется в DLQ.

## API

- `GET /api/v1/notifications`
- `GET /api/v1/notifications/unread`
- `POST /api/v1/notifications/{id}/read`
- `POST /api/v1/notifications/read-all`
- `GET /health`
- `GET /ready`
- `GET /metrics`
