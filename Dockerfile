# Use Python 3.10 to ensure compatibility with newer Django and django-filter versions
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY jwt_auth/requirements.txt .

# Install system dependencies and Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Make entrypoint.sh executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Collect static files to the STATIC_ROOT (this is required for production)
RUN python manage.py collectstatic --noinput

# Ensure celery is installed
RUN pip install --no-cache-dir celery

# Expose the port that Django will run on
EXPOSE 8000

# Start the application using the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

