# backend/app/config.py
import os
from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    APP_NAME: str = "ftaas-backend"
    DATA_DIR: str = os.environ.get("DATA_DIR", "/data/uploads")
    MODEL_DIR: str = os.environ.get("MODEL_DIR", "/data/model_cache")
    
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    MODEL_CACHE_DIR: str = os.getenv("MODEL_CACHE_DIR", "/data/model_cache")

    # Postgres
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL", "postgresql+psycopg2://postgres:postgres@postgres:5432/ftaas"
    )

    # Celery / RabbitMQ
    BROKER_URL: str = os.environ.get("BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")
    RESULT_BACKEND: str = os.environ.get("RESULT_BACKEND", "rpc://")

    # App settings
    MAX_UPLOAD_SIZE_MB: int = int(os.environ.get("MAX_UPLOAD_SIZE_MB", "200"))

    class Config:
        env_file = ".env"


settings = Settings()
