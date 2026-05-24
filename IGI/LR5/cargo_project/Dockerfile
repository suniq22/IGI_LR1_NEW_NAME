FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app

RUN mkdir -p /app/logs /app/media /app/staticfiles

EXPOSE 8000

# $PORT is provided by Railway/Render/Heroku; defaults to 8000 locally / in docker-compose.
CMD ["sh", "-c", "python manage.py migrate --noinput && (python manage.py collectstatic --noinput || true) && gunicorn cargo_project.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 120"]
