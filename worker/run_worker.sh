#!/bin/bash
celery -A app.tasks.celery_app worker --loglevel=info --concurrency=1
