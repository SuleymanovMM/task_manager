from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "taskflow-notification"
    environment: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8003
    log_level: str = "INFO"

    database_url: str = "postgresql+asyncpg://task:task@localhost:5432/notification_db"

    jwt_public_key_path: str = "./secrets/public.pem"
    jwt_algorithm: str = "RS256"
    identity_service_url: str = "http://identity-service:8000"

    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "taskflow.events"
    rabbitmq_dlx_exchange: str = "taskflow.events.dlq"
    rabbitmq_queue: str = "notification-service.notifications"
    rabbitmq_dlq: str = "notification-service.notifications.dlq"
    rabbitmq_max_retries: int = 3
    consumer_name: str = "notification-service"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
