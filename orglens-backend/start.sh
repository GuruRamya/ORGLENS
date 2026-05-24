#!/bin/bash

echo "Starting OrgLens..."
echo "PORT is: $PORT"

nohup celery -A app.workers.celery_app worker --loglevel=info --concurrency=1 > /tmp/celery.log 2>&1 &

echo "Celery started with PID $!"

echo "Starting uvicorn on port $PORT"
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
