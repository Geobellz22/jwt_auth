#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Daphne server
echo "Starting Daphne server..."
exec daphne -b 0.0.0.0 -p 8000 jwt_auth.asgi:application
