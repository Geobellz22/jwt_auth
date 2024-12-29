#!/bin/sh

# Set the DJANGO_SETTINGS_MODULE environment variable
export DJANGO_SETTINGS_MODULE=jwt_auth.settings

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Start Daphne server
exec daphne -b 0.0.0.0 -p 8000 jwt_auth.asgi:application
