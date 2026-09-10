# TaskFlow Task Service

Bounded context «Задачи» для TaskFlow/TaskManager.

## Зона ответственности

- CRUD задач и переходы статусов.
- Назначение исполнителя и проверка членства в проекте через Project Service.
- Комментарии и история изменений.
- Redis cache-aside для `GET /api/v1/tasks/{id}`.
- Агрегация статистики по проекту в PostgreSQL.
- Transactional Outbox + события RabbitMQ.

К `identity_db` и `project_db` сервис не подключается.

## Запуск локально

```bash
cp .env.example .env
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8002
```

Тестовые инструменты (`pytest`, `pytest-asyncio`) не входят в `requirements.txt` — ставятся в venv отдельно.

`secrets/public.pem` должен быть тем же ключом, что и у Identity Service.

## Docker

Сервис уже подключён в корневой `../../docker-compose.yml` (две реплики за nginx, общая `task_db`). Публичный ключ в образе — только для разработки; в проде монтируйте его как read-only secret.

## Миграции

```bash
alembic upgrade head
```

## События

Событие пишется в `outbox_events` в той же транзакции, что и изменение задачи. Фоновый воркер публикует неопубликованные события в RabbitMQ и помечает их опубликованными только после успешной отправки.

Публикуемые типы событий:

- `TaskCreated`
- `TaskAssigned`
- `TaskStatusChanged`
- `TaskCompleted`
- `TaskDeadlineChanged`

## Авторизация

JWT проверяется локально по публичному ключу Identity — обращения к самому Identity не требуется. Для проверки роли в проекте сервис вызывает:

`GET /api/v1/internal/projects/{project_id}/members/{user_id}`

Роли в проекте:

- OWNER / MANAGER: создание, изменение, назначение, отмена задач.
- OWNER / MANAGER или назначенный исполнитель: смена статуса задачи.
- Любой участник проекта: просмотр задач, комментариев, истории.
- Автор комментария: редактирование/удаление своего комментария.
