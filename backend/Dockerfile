FROM python:3.11-slim

WORKDIR /app

# system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev gcc wget && rm -rf /var/lib/apt/lists/*

# copy code
COPY ./app /app/app
COPY requirements.txt /app/requirements.txt

# install python deps
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

ENV PYTHONPATH=/app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
