from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import Field

class Settings(BaseSettings):
    app_name: str = "OrgLens"
    app_version: str = "1.0.0"
    debug: bool = False
    secret_key: str = "change-me-in-production"
    database_url: str
    redis_url: str
    GROQ_API_KEY: str = Field(default="", alias="GROQ_API_KEY")
    celery_broker_url: str
    celery_result_backend: str
    slack_client_id: str = ""
    slack_client_secret : str = ""
    slack_redirect_uri: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""
    frontend_url: str = "http://localhost:5173"
    upload_dir: str = "./uploads"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
