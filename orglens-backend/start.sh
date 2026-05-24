#!/bin/bash

celery -A app.workers.celery_app worker --loglevel=info --concurrency=1 --detach

sleep 2

exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
