#!/bin/sh

# Set Python path to include current directory
export PYTHONPATH="${PYTHONPATH}:/src"

# Wait for MySQL to be ready
echo "Waiting for MySQL..."
while ! nc -z db 3306; do
  sleep 1
done
echo "MySQL is ready!"

# Wait for Redis
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 1
done
echo "Redis is ready!"

# Wait for RabbitMQ
echo "Waiting for RabbitMQ..."
while ! nc -z broker 5672; do
  sleep 1
done
echo "RabbitMQ is ready!"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create cache table
echo "Creating cache table..."
python manage.py createcachetable

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the application
echo "Starting application..."
exec "$@" 