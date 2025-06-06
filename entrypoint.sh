#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Make database migrations
echo "Making database migrations..."
python manage.py makemigrations --noinput

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

python manage.py spectacular --color --file schema.yml
# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput


# Start Daphne server
echo "Starting Daphne server..."
exec daphne -b 0.0.0.0 -p 8000 jwt_auth.asgi:application
