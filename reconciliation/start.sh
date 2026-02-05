#!/bin/bash

python manage.py migrate

if [ ! -d "/app/data/static" ] || [ -z "$(ls -A /app/data/static)" ]; then
    python manage.py collectstatic --noinput
else
    echo "Static files already exist, skipping collectstatic"
fi

exec gunicorn --bind 0.0.0.0:8000 reconciliation.wsgi:application