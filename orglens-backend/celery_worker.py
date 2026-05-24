"""
Celery worker script.
Run with: celery -A app.workers worker --loglevel=info
"""

import sys
import os
from loguru import logger

sys.path.insert(0, os.path.dirname(__file__))

from app.workers import celery_app
from app.workers.analysis_tasks import analyze_organization

logger.remove()
logger.add(
    "logs/celery_worker.log",
    rotation="500 MB",
    retention="10 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

if __name__ == "__main__":
    celery_app.start()
