# TaskManager

Менеджер задач на микросервисах: регистрация/аутентификация, проекты и команды, задачи с историей и комментариями, уведомления о событиях — каждый в своей зоне ответственности, за общим nginx.

## Архитектура

| Сервис | Порт (хост) | Отвечает за |
|---|---|---|
| identity | 8001 | Регистрация, вход, JWT (RS256), refresh-токены, rate limiting |
| project | 8002 | Проекты, команды, участники, приглашения |
| task | 8003 / 8004 (2 реплики) | Задачи, статусы, комментарии, история, статистика |
| notification | 8005 | Уведомления по событиям из RabbitMQ |

Плюс nginx (порт 80, единая точка входа), PostgreSQL — своя база на сервис, Redis (identity, task), RabbitMQ (project → task → notification), Prometheus (порт 9090).

**Ключевые решения:**
- JWT проверяется локально по публичному RS256-ключу identity — остальные сервисы не ходят в identity за каждым запросом.
- У каждого сервиса своя БД; `user_id`/`project_id` между сервисами — логические UUID-ссылки, без FK.
- `project` и `task` публикуют события в RabbitMQ (`ProjectMemberAdded`, `TaskAssigned` и т.д.), `notification` их читает и идемпотентно создаёт уведомления.
- `task-service` поднят в двух репликах за одним nginx-апстримом — миграции гоняет только первая.

Детали и полный список эндпоинтов каждого сервиса — в `services/<name>/README.md`.

## Быстрый старт

Требуется Docker и Docker Compose.

```bash
git clone https://github.com/SuleymanovMM/task_manager.git
cd task_manager
```

Сгенерировать пару JWT-ключей (приватный не коммитится, в репозитории его нет):

```bash
cd services/identity && ./scripts/generate_keys.sh   # или generate_keys.ps1 на Windows
cd ../..
```

Скопировать публичный ключ туда, где его ждут остальные сервисы:

```bash
cp services/identity/secrets/public.pem services/project/secrets/public.pem
cp services/identity/secrets/public.pem services/task/secrets/public.pem
cp services/identity/secrets/public.pem services/notification/secrets/public.pem
```

Собрать и поднять весь стек:

```bash
make build && make up
# или без make: docker compose build && docker compose up -d
```

Проверить, что всё поднялось:

```bash
docker compose ps
curl http://localhost/health
```

API доступно через nginx на `http://localhost` (например, `POST /api/v1/auth/register`). Миграции применяются автоматически при старте контейнеров; переприменить вручную на уже запущенном стеке — `make migrate-all`.

Остановить и удалить (вместе с данными в volume'ах):

```bash
make down
```

## Тестирование

У каждого сервиса свой venv и `requirements.txt` — тестовые зависимости (`pytest`, `pytest-asyncio`) в них не входят и ставятся отдельно.

```bash
cd services/identity
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt          # Linux/Mac: .venv/bin/pip
.venv/Scripts/pip install pytest pytest-asyncio
.venv/Scripts/python -m pytest tests/ -q
```

Так же для `project`, `task` (дополнительно `httpx`) и `notification` (дополнительно `httpx`, `aiosqlite`). Интеграционные тесты `identity` и `task` поднимают временный PostgreSQL/Redis — при их отсутствии соответствующие тесты пропускаются, а не падают.

В образах сервисов `pytest` не установлен (они собраны только под прод-зависимости), поэтому тесты гоняются локально через venv, а не `docker compose exec`.

## Структура репозитория

```
services/
  identity/       # аутентификация, JWT, RS256-ключи
  project/        # проекты, команды, приглашения
  task/           # задачи, комментарии, история, статистика
  notification/   # консьюмер RabbitMQ → уведомления
nginx/            # реверс-прокси и роутинг
infrastructure/   # конфиг Prometheus
docker-compose.yml
Makefile
```

## Мониторинг

- Prometheus: `http://localhost:9090`
- RabbitMQ management UI: `http://localhost:15672` (guest/guest)
- `/metrics` в формате Prometheus — на каждом сервисе
