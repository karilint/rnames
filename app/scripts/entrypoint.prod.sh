#!/bin/sh

set -e

python manage.py migrate --no-input
python manage.py collectstatic --no-input

celery -A main worker --detach -l INFO
gunicorn main.wsgi:application --bind 0.0.0.0:8000
