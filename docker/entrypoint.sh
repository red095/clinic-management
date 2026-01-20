#!/bin/bash
# wait for postgres
echo "Waiting for Postgres..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "Postgres started"

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start server
echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
