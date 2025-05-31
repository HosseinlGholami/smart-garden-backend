# 🌐 Environment Configuration Guide

This document explains how to configure environment variables for the Smart Garden Backend.

## 📁 Environment Files

The project uses different environment files for different deployment scenarios:

- **`env.example`** - Template with all available variables and documentation
- **`.env`** - Current environment configuration (production/staging)
- **`env.development`** - Development environment defaults
- **`.env.local`** - Local overrides (not tracked in git)

## 🔧 Setup Instructions

### For Development
1. Copy the development template:
   ```bash
   cp env.development .env
   ```

2. Adjust values as needed for your local setup

### For Production
1. Copy the example template:
   ```bash
   cp env.example .env
   ```

2. Generate a secure SECRET_KEY:
   ```bash
   python -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)') for i in range(64)))"
   ```

3. Update all production values

## 🔐 Critical Security Variables

### SECRET_KEY
- **Required**: Yes
- **Description**: Django secret key for cryptographic signing
- **Length**: Minimum 50 characters, recommended 64
- **Production**: Must be unique and secure
- **Development**: Auto-generated if not provided

### DEBUG
- **Values**: `0` (False) or `1` (True)
- **Production**: Must be `0`
- **Development**: Can be `1`
- **Security**: Never enable in production

## 🗄️ Database Configuration

### MySQL Settings
```bash
DB_ENGINE=django.db.backends.mysql
DB_NAME=smart_garden
DB_USER=root
DB_PASSWORD=your-secure-password
DB_HOST=db
DB_PORT=3306
```

## 🌐 Network Configuration

### Server Settings
```bash
LOCAL_IP=your-server-ip
DJANGO_ALLOWED_HOSTS=domain1.com domain2.com
CORS_ALLOWED_ORIGINS=https://frontend.com,https://app.com
```

### CORS Configuration
- **Development**: Include localhost origins
- **Production**: Only include actual domains
- **Format**: Comma-separated list of full URLs

## 📨 Message Queue (RabbitMQ)

### Connection Settings
```bash
RABBITMQ_HOST=broker
RABBITMQ_PORT=5672
RABBITMQ_USER=your-username
RABBITMQ_PASS=your-password
RABBITMQ_VHOST=/
```

## 📊 InfluxDB (Time-Series Database)

### Configuration
```bash
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_TOKEN=your-influxdb-token
INFLUXDB_ORG=smart-garden
INFLUXDB_BUCKET=sensor-data
```

## 🔄 Celery Configuration

### Basic Settings
```bash
FLOWER_BASE_URL=http://celery:6666/flower
FLOWER_USER=admin
FLOWER_PASSWORD=secure-password
C_FORCE_ROOT=true
```

## 🧪 Environment-Specific Configurations

### Development
- Auto-generated SECRET_KEY
- DEBUG=1
- Localhost CORS origins
- Development database name
- Console email backend

### Staging
- Secure SECRET_KEY
- DEBUG=0
- Staging domain CORS
- Staging database
- Email notifications enabled

### Production
- Secure SECRET_KEY
- DEBUG=0
- Production domains only
- Production database
- Full monitoring enabled

## 🔒 Security Best Practices

### Secret Management
1. Never commit `.env` files to version control
2. Use environment-specific files
3. Rotate secrets regularly
4. Use strong passwords (min 16 characters)
5. Enable 2FA where possible

### Production Checklist
- [ ] SECRET_KEY is 64+ characters and unique
- [ ] DEBUG=0
- [ ] ALLOWED_HOSTS contains only your domains
- [ ] Database passwords are strong
- [ ] API keys are production values
- [ ] CORS origins are restricted
- [ ] HTTPS is enabled

## 🚀 Deployment

### Docker Compose
The `docker-compose.yml` file automatically loads the `.env` file:

```yaml
services:
  app:
    env_file:
      - .env
```

### Environment Variables Priority
1. Environment variables set in shell
2. Variables in `.env` file
3. Default values in `settings.py`

### Validation
Test your configuration:
```bash
docker compose exec app python manage.py test users.test_security
```

## 🔍 Troubleshooting

### Common Issues

**SECRET_KEY too short**
```
Error: SECRET_KEY must be at least 50 characters long
```
Solution: Generate a new 64-character key

**CORS errors**
```
Error: CORS origin not allowed
```
Solution: Add your frontend URL to CORS_ALLOWED_ORIGINS

**Database connection failed**
```
Error: Can't connect to MySQL server
```
Solution: Check DB_HOST, DB_PORT, DB_USER, DB_PASSWORD

### Debug Commands
```bash
# Check environment variables
docker compose exec app python -c "from django.conf import settings; print(f'DEBUG: {settings.DEBUG}')"

# Test database connection
docker compose exec app python manage.py migrate --dry-run

# Validate settings
docker compose exec app python manage.py check

# Test security configuration
docker compose exec app python manage.py test users.test_security
```

## 📚 Additional Resources

- [Django Settings Documentation](https://docs.djangoproject.com/en/stable/topics/settings/)
- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [Docker Environment Variables](https://docs.docker.com/compose/environment-variables/)
- [Celery Configuration](https://docs.celeryproject.org/en/stable/userguide/configuration.html) 