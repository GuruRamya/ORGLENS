from celery import Celery
from app.config import settings
import app.workers.analysis_tasks
celery_app = Celery(
    "orglens",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# 🔥 THIS LINE FIXES YOUR ERROR
celery_app.autodiscover_tasks(["app.workers"])

# Optional but recommended
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
)