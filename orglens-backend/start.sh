#!/bin/bash

# Start Celery worker in background
celery -A app.workers.celery_app worker --loglevel=info --concurrency=1 --detach

# Wait a moment for celery to initialize
sleep 2

# Start FastAPI on the port Render provides
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
