#!/bin/sh

# Apply database migrations
python manage.py migrate

# Start Daphne server
exec daphne -b 0.0.0.0 -p 8000 jwt_auth.asgi:application
 
 The  entrypoint.sh  script is responsible for applying database migrations and starting the Daphne server. 
 The  Dockerfile  is used to build the Docker image.