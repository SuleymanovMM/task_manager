# TaskFlow Project Service

Bounded context «Проекты и команды» для TaskFlow.

## Зона ответственности

- Проекты, команды, участники проектов, приглашения.
- Самостоятельная проверка RS256 access-JWT по публичному ключу.
- События RabbitMQ `ProjectMemberAdded`, `ProjectInvitationCreated`.
- Своя `project_db`; `user_id`/`owner_id` — логические UUID-ссылки, не FK на Identity.

## Запуск

Скопируйте `.env.example` в `.env`, положите публичный ключ Identity в `secrets/public.pem`, затем:

```powershell
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8001
```

Тестовые инструменты (`pytest`, `pytest-asyncio`) не входят в `requirements.txt` — ставятся в venv отдельно.

## Docker

```powershell
docker compose up --build
```

Сервис уже подключён в корневой `../../docker-compose.yml`, в одной сети с PostgreSQL и RabbitMQ.

## Эндпоинты

- Проекты: `/api/v1/projects`
- Команды: `/api/v1/teams`
- Участники проекта: `/api/v1/projects/{id}/members`
- Приглашения: `/api/v1/projects/{id}/invitations`, `/api/v1/invitations`
- Внутренняя проверка членства: `/api/v1/internal/projects/{id}/members/{user_id}`
- Health: `/health`, `/ready`, `/metrics`

## Архитектура

HTTP/API → application services → domain → интерфейсы репозиториев → SQLAlchemy.

JWT проверяется локально по публичному ключу Identity, без обращения к самому Identity.
