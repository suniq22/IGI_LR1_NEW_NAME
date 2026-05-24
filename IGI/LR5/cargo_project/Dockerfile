FROM python:3.12-slim

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
# Keep a seed copy of media files (volume mount shadows /app/media at runtime)
RUN cp -r /app/media /app/media_seed

# collect static files at build time (no DB needed)
RUN DJANGO_SECRET_KEY=build-dummy DJANGO_DEBUG=False python manage.py collectstatic --noinput

EXPOSE 8000

# $PORT is provided by Railway/Render/Heroku; defaults to 8000 locally / in docker-compose.
CMD ["sh", "-c", "if [ -z \"$(ls -A /app/media 2>/dev/null)\" ]; then cp -r /app/media_seed/. /app/media/; fi ; python manage.py migrate --noinput ; python manage.py createsuperuser --noinput --skip-checks 2>/dev/null || true ; python manage.py shell -c \"from django.contrib.auth.models import User; exit(0 if User.objects.count() > 1 else 1)\" 2>/dev/null || python manage.py loaddata fixtures/initial_data.json --ignorenonexistent ; gunicorn cargo_project.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 120"]
