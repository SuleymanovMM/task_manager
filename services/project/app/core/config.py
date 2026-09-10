from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "taskflow-project"
    environment: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8001
    log_level: str = "INFO"
    database_url: str = "postgresql+asyncpg://project:project@localhost:5432/project_db"
    jwt_public_key_path: str = "./secrets/public.pem"
    jwt_algorithm: str = "RS256"
    identity_service_url: str = "http://identity-service:8000"
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"
    rabbitmq_exchange: str = "taskflow.events"
    cors_origins: str = ""
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
