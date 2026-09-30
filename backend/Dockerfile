FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Placeholder values so `collectstatic` can import settings.py at build time (it requires these
# env vars to be set but doesn't need real ones). The deployment platform's real env vars
# override these at container runtime.
ENV DJANGO_SECRET_KEY=build-time-placeholder \
    DATABASE_URL=postgresql://user:password@localhost:5432/placeholder \
    CORS_ALLOWED_ORIGINS=http://localhost

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD sh -c "python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}"
