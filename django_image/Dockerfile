FROM python:3.10-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=core.settings

# Set work directory
WORKDIR /src

# Install system dependencies
RUN apk add --no-cache \
    postgresql-dev \
    gcc \
    python3-dev \
    musl-dev \
    libffi-dev \
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    tiff-dev \
    tk-dev \
    tcl-dev \
    harfbuzz-dev \
    fribidi-dev \
    mariadb-dev \
    mariadb-connector-c-dev \
    build-base \
    curl \
    netcat-openbsd

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Daphne and Channels explicitly
RUN python -m pip install -U "channels[daphne]"

# Create necessary directories
RUN mkdir -p /src/static /src/media /var/run/celery

# Copy and set up entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create a non-root user and change ownership
RUN adduser -D user && \
    chown -R user:user /src /var/run/celery /entrypoint.sh

# Switch to non-root user
USER user

ENTRYPOINT ["/entrypoint.sh"]