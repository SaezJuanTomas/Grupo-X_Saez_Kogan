from pydantic_settings import BaseSettings


class Config(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5435/grupo_x"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    RATE_LIMIT_LOGIN: str = "5/15minutes"
    N8N_API_KEY: str = "change-me-n8n-api-key"
    N8N_WEBHOOK_URL: str = "http://localhost:5678/webhook/trigger-nvd-fetch"
    NVD_API_KEY: str = ""
    LOG_LEVEL: str = "INFO"

    model_config = {"env_file": ".env", "extra": "ignore"}


config = Config()
