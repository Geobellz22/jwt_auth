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

# Expose the port that Django will run on
EXPOSE 8000

# Run Django development server (modify as needed for production)
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

COPY . .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]