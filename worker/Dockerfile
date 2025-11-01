FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y python3 python3-pip git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy backend requirements (path relative to docker-compose context, not Dockerfile)
COPY ./backend/requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# copy backend app (again relative to compose context)
COPY ./backend/app /app/app

ENV PYTHONPATH=/app

CMD ["bash", "-lc", "celery -A app.tasks.celery_app worker --loglevel=info --concurrency=1"]
