from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "taskflow-task"
    environment: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8002
    log_level: str = "INFO"

    database_url: str = "postgresql+asyncpg://task:task@localhost:5432/task_db"

    jwt_public_key_path: str = "./secrets/public.pem"
    jwt_algorithm: str = "RS256"
    identity_service_url: str = "http://identity-service:8000"

    project_service_url: str = "http://project:8001"
    project_service_timeout_seconds: float = 5.0
    project_service_retries: int = 1

    redis_url: str = "redis://redis:6379/0"
    redis_ttl_seconds: int = 300
    project_member_cache_ttl_seconds: int = 60

    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"
    rabbitmq_exchange: str = "taskflow.events"
    outbox_poll_seconds: float = 1.0

    cors_origins: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
