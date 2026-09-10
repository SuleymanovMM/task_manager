.PHONY: up down build logs \
	shell-identity shell-project shell-task shell-notification \
	migrate-identity migrate-project migrate-task migrate-notification migrate-all

# ─── Docker Compose ───
up:
	docker compose up -d

down:
	docker compose down -v

build:
	docker compose build

logs:
	docker compose logs -f

# ─── Сервисы ───
shell-identity:
	docker compose exec identity-service sh

shell-project:
	docker compose exec project-service sh

shell-task:
	docker compose exec task-service-1 sh

shell-notification:
	docker compose exec notification-service sh

# ─── База данных ───
migrate-identity:
	docker compose exec identity-service alembic upgrade head

migrate-project:
	docker compose exec project-service alembic upgrade head

migrate-task:
	docker compose exec task-service-1 alembic upgrade head

migrate-notification:
	docker compose exec notification-service alembic upgrade head

migrate-all: migrate-identity migrate-project migrate-task migrate-notification
