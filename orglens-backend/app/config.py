from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import Field

class Settings(BaseSettings):
    # App
    app_name: str = "OrgLens"
    app_version: str = "1.0.0"
    debug: bool = False
    secret_key: str = "change-me-in-production"

    # Database
    database_url: str

    # Redis (general)
    redis_url: str
    GROQ_API_KEY: str = Field(default="", alias="GROQ_API_KEY")
    # Celery (IMPORTANT ADD THIS)
    celery_broker_url: str
    celery_result_backend: str

    # Slack
    slack_client_id: str = ""
    slack_client_secret : str = ""
    slack_redirect_uri: str = ""

    # Google
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""

    # CORS
    frontend_url: str = "http://localhost:5173"

    # Uploads
    upload_dir: str = "./uploads"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()