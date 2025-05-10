#!/bin/bash

# Exit on error
set -e

# Wait for database to be ready
echo "Waiting for database..."
python -c "
import sys
import time
import psycopg2

# Maximum number of attempts
max_attempts = 30
attempt = 0

while attempt < max_attempts:
    try:
        psycopg2.connect(
            dbname='${DB_NAME}',
            user='${DB_USER}',
            password='${DB_PASSWORD}',
            host='${DB_HOST}',
            port='${DB_PORT}'
        )
        break
    except psycopg2.OperationalError:
        attempt += 1
        print(f'Waiting for database... {attempt}/{max_attempts}')
        time.sleep(1)

if attempt == max_attempts:
    print('Database connection failed')
    sys.exit(1)

print('Database connection established')
"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files (only if not in development mode)
if [ "$DEBUG" != "True" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput || {
        echo "Warning: collectstatic command failed, but continuing anyway..."
    }
else
    echo "Skipping collectstatic in development mode..."
fi

# Create superuser if needed
echo "Creating superuser if needed..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_api.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')

if not User.objects.filter(username=username).exists():
    print(f'Creating superuser {username}...')
    User.objects.create_superuser(username=username, email=email, password=password)
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"

# Initialize PIDS array if not already defined
PIDS=()

# Only start Celery if we're not running in the dedicated Celery containers
if [[ "$1" != "celery" ]]; then
    # Check if we should start Celery in the web container (for single container deployments)
    if [[ "$START_CELERY_IN_WEB" == "True" ]]; then
        echo "Starting Celery worker in web container..."
        celery -A ecommerce_api worker --loglevel=info &
        PIDS+=($!)

        echo "Starting Celery beat in web container..."
        celery -A ecommerce_api beat --loglevel=info &
        PIDS+=($!)
    else
        echo "Skipping Celery startup in web container (using dedicated Celery containers)..."
    fi
fi

# Execute the command passed to the script
exec "$@"
