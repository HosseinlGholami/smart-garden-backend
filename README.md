# 🌿 Smart Garden Watering Automation System

A comprehensive IoT-based smart irrigation system using ESP32, MQTT, Django REST API, and Next.js frontend. This system enables remote garden monitoring and control with real-time status updates, automated scheduling, and mobile-friendly interface.

## 📋 Table of Contents

- [🏗️ Architecture Overview](#️-architecture-overview)
- [🚀 Features](#-features)
- [📂 Project Structure](#-project-structure)
- [🛠️ Technology Stack](#️-technology-stack)
- [⚙️ Installation & Setup](#️-installation--setup)
- [🔧 Configuration](#-configuration)
- [📱 Frontend Application](#-frontend-application)
- [🔌 Backend API](#-backend-api)
- [🏗️ Infrastructure](#️-infrastructure)
- [🔄 Development Workflow](#-development-workflow)
- [📊 Monitoring & Logging](#-monitoring--logging)
- [🔐 Security](#-security)
- [🧪 Testing](#-testing)
- [📚 API Documentation](#-api-documentation)
- [🤝 Contributing](#-contributing)

## 🏗️ Architecture Overview

The Smart Garden system follows a microservices architecture with the following components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ESP32 Nodes   │    │   Frontend      │    │   Mobile App    │
│   (IoT Devices) │    │   (Next.js)     │    │   (PWA)         │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │ MQTT                 │ HTTP/WS              │ HTTP/WS
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Nginx Reverse Proxy                      │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   Django API    │ │   RabbitMQ      │ │   InfluxDB      │
│   (Backend)     │ │   (MQTT Broker) │ │   (Time Series) │
└─────────┬───────┘ └─────────────────┘ └─────────────────┘
          │
          ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│     MySQL       │ │     Redis       │ │     Celery      │
│   (Database)    │ │    (Cache)      │ │   (Tasks)       │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## 🚀 Features

### 🎛️ Real-time Control & Monitoring
- **Live Dashboard**: Real-time status of valves, pump, and power systems
- **Manual Control**: Instant valve and pump control via web interface
- **System Status**: Connection monitoring, battery levels, and health checks
- **WebSocket Updates**: Real-time data streaming without page refresh

### ⏰ Automated Scheduling
- **Flexible Scheduling**: Daily, weekly, or one-time watering schedules
- **Multi-zone Support**: Independent control of up to 4 garden zones
- **Duration Control**: Customizable watering duration per zone
- **Background Tasks**: Celery-powered automated execution

### 📊 Data Analytics & Visualization
- **Water Usage Tracking**: Historical consumption data with charts
- **Power Monitoring**: Real-time and historical power consumption
- **System Logs**: Comprehensive event logging with filtering
- **Performance Metrics**: System health and efficiency tracking

### 🔐 User Management & Security
- **Role-based Access**: Admin, Manager, and Staff user roles
- **Garden Access Control**: Multi-user garden management
- **JWT Authentication**: Secure API access with token-based auth
- **Guest Mode**: Demo access with mock data for testing

### 📱 Mobile-First Design
- **Responsive UI**: Optimized for desktop, tablet, and mobile
- **PWA Support**: Progressive Web App capabilities
- **Touch-friendly**: Mobile-optimized controls and navigation
- **Offline Capability**: Basic functionality without internet

## 📂 Project Structure

This repository contains three main components organized as Git submodules:

```
smart-garden-backend/
├── 📁 app/                          # Django Backend Application
│   ├── 📁 core/                     # Django project settings
│   │   ├── settings.py              # Main configuration
│   │   ├── urls.py                  # URL routing
│   │   ├── asgi.py                  # ASGI configuration for WebSockets
│   │   └── routing.py               # WebSocket routing
│   ├── 📁 garden/                   # Garden management app
│   │   ├── models.py                # Database models
│   │   ├── views.py                 # API endpoints
│   │   ├── serializers.py           # Data serialization
│   │   ├── permissions.py           # Access control
│   │   └── urls.py                  # Garden API routes
│   ├── 📁 users/                    # User authentication app
│   │   ├── models.py                # Custom user model
│   │   ├── serializers.py           # User data serialization
│   │   └── views.py                 # Auth endpoints
│   └── 📁 tasks/                    # Celery background tasks
│       └── tasks.py                 # Scheduled task definitions
├── 📁 django_image/                 # Docker configuration for Django
│   ├── Dockerfile                   # Django container definition
│   ├── requirements.txt             # Python dependencies
│   └── entrypoint.sh               # Container startup script
├── 📁 smart-garden-front/           # Frontend Submodule (Next.js)
│   ├── 📁 app/                      # Next.js app directory
│   │   ├── 📁 (dashboard)/          # Dashboard pages
│   │   │   ├── dashboard/           # Main dashboard
│   │   │   ├── manual-control/      # Manual control interface
│   │   │   ├── schedule/            # Scheduling interface
│   │   │   ├── settings/            # System settings
│   │   │   └── logs/               # System logs viewer
│   │   ├── 📁 (auth)/              # Authentication pages
│   │   ├── 📁 components/          # React components
│   │   └── 📁 lib/                 # Utilities and API client
│   ├── 📁 components/              # Shared UI components
│   └── package.json                # Node.js dependencies
├── 📁 smart-garden-infra/          # Infrastructure Submodule
│   ├── docker-compose.yml          # Infrastructure services
│   ├── 📁 nginx_image/             # Nginx configuration
│   ├── 📁 mysql_image/             # MySQL initialization
│   ├── 📁 redis_image/             # Redis configuration
│   └── 📁 rbmq_image/              # RabbitMQ configuration
├── docker-compose.yml              # Main orchestration file
├── .env                            # Environment variables
└── README.md                       # This documentation
```

## 🛠️ Technology Stack

### 🔧 Backend Technologies
- **Framework**: Django 5.0.1 with Django REST Framework
- **Database**: MySQL 8.0.32 for persistent data storage
- **Cache**: Redis 8-alpine for session management and caching
- **Message Broker**: RabbitMQ 3.13.5 with MQTT plugin
- **Task Queue**: Celery 5.3.6 for background job processing
- **Time Series DB**: InfluxDB 2.7 for sensor data storage
- **WebSockets**: Django Channels 4.0.0 with Daphne ASGI server

### 🎨 Frontend Technologies
- **Framework**: Next.js 15.2.4 with React 19
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS 4 with shadcn/ui components
- **Charts**: Recharts 2.15.3 for data visualization
- **Icons**: Lucide React 0.511.0
- **State Management**: React Hooks and Context API

### 🏗️ Infrastructure & DevOps
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx 1.28.0 as reverse proxy
- **Monitoring**: Prometheus metrics integration
- **Process Management**: Celery Beat for scheduled tasks
- **Development**: Hot reload and live debugging support

### 📡 IoT & Communication
- **Hardware**: ESP32 microcontrollers
- **Protocol**: MQTT over RabbitMQ broker
- **Data Format**: JSON for sensor data and commands
- **Real-time**: WebSocket connections for live updates

## ⚙️ Installation & Setup

### 📋 Prerequisites
- Docker 20.10+ and Docker Compose 2.0+
- Git with submodule support
- 4GB+ RAM for all services
- 10GB+ disk space

### 🚀 Quick Start

1. **Clone the repository with submodules**:
   ```bash
   git clone --recurse-submodules https://github.com/HosseinlGholami/smart-garden-backend.git
   cd smart-garden-backend
   ```

2. **If already cloned, initialize submodules**:
   ```bash
   git submodule update --init --recursive
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Build and start all services**:
   ```bash
   docker-compose up -d
   ```

5. **Access the application**:
   - **Web Interface**: http://localhost
   - **API Documentation**: http://localhost/api/docs/
   - **Admin Panel**: http://localhost/admin/
   - **RabbitMQ Management**: http://localhost:15672
   - **Flower (Celery Monitor)**: http://localhost:5555

### 🔄 Development Setup

For local development with hot reload:

1. **Start infrastructure services**:
   ```bash
   docker-compose up -d db redis broker influxdb
   ```

2. **Run Django backend locally**:
   ```bash
   cd app
   pip install -r ../django_image/requirements.txt
   python manage.py migrate
   python manage.py runserver 8000
   ```

3. **Run Next.js frontend locally**:
   ```bash
   cd smart-garden-front
   npm install
   npm run dev
   ```

## 🔧 Configuration

### 🌍 Environment Variables

The `.env` file contains all configuration options:

```bash
# Server Configuration
LOCAL_IP=185.252.86.186
ENVIRONMENT=production
DEBUG=1

# Database Configuration
DB_ENGINE=django.db.backends.mysql
DB_NAME=smart_garden
DB_USER=root
DB_PASSWORD=root
DB_HOST=db
DB_PORT=3306

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# RabbitMQ Configuration
CELERY_BROKER_URL=amqp://guest:guest@broker:5672//

# InfluxDB Configuration
INFLUXDB_TOKEN=your_influxdb_token_here
INFLUXDB_ORG=smart_garden
INFLUXDB_BUCKET=sensor_data

# Security
SECRET_KEY=your_django_secret_key_here
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 185.252.86.186 haj-ebram.ir

# External Services
SSO_URL=http://185.252.86.186/oauth
FLOWER_BASE_URL=http://celery:6666/flower
```

### 🔐 Security Configuration

- **CORS Settings**: Configured for production domains
- **CSRF Protection**: Enabled with trusted origins
- **JWT Tokens**: 1-day access, 7-day refresh tokens
- **User Roles**: Admin, Manager, Staff with granular permissions

## 📱 Frontend Application

### 🎨 User Interface

The frontend is built with Next.js 15 and provides a modern, responsive interface:

#### 📊 Dashboard (`/dashboard`)
- Real-time system status overview
- Live valve, pump, and power status
- Connection monitoring with ESP32 nodes
- Next scheduled watering events
- System health indicators

#### 🎛️ Manual Control (`/manual-control`)
- Individual valve control with duration settings
- Pump start/stop functionality
- Emergency stop for all systems
- Real-time status updates
- Duration timers and countdowns

#### ⏰ Schedule Management (`/schedule`)
- Create, edit, and delete watering schedules
- Daily, weekly, and one-time scheduling options
- Multi-zone scheduling support
- Schedule activation/deactivation
- Visual schedule calendar

#### 📋 System Logs (`/logs`)
- Comprehensive event logging
- Filter by source (Manual, Automatic, System)
- Date range filtering
- Real-time log updates
- Export functionality

#### ⚙️ Settings (`/settings`)
- User profile management
- System configuration
- Garden access management
- Notification preferences

### 🔄 State Management

The frontend uses React hooks and context for state management:

```typescript
// API Client with mock data support
export const shouldUseMockAPI = () => {
  const isClientSide = typeof window !== 'undefined'
  const localStorageMockSetting = isClientSide ? 
    localStorage.getItem('useMockData') === 'true' : false
  return ENV.API.USE_MOCK || localStorageMockSetting
}

// Real-time data fetching
useEffect(() => {
  async function fetchDashboardData() {
    const [systemData, valveData, powerData, pumpData] = await Promise.all([
      getSystemStatus(),
      getValveStatus(),
      getPowerStatus(),
      getPumpStatus(),
    ])
    // Update state...
  }
  
  fetchDashboardData()
  const refreshInterval = setInterval(fetchDashboardData, 30000)
  return () => clearInterval(refreshInterval)
}, [])
```

### 🎭 Mock Data System

For development and demonstration, the frontend includes comprehensive mock data:

```typescript
export const MOCK_DATA = {
  systemStatus: {
    isConnected: true,
    nextSchedule: { time: "18:00", target: "Evening Garden" },
    lastChecked: new Date().toISOString()
  },
  valveStatus: [
    { id: 1, name: "Lawn Zone 1", status: "closed", duration: 300 },
    { id: 2, name: "Garden Beds", status: "open", duration: 600 },
    // ... more valves
  ],
  // ... comprehensive mock data for all endpoints
}
```

## 🔌 Backend API

### 🏗️ Django Application Structure

The backend is organized into Django apps with clear separation of concerns:

#### 🌱 Garden App (`app/garden/`)

**Models**:
- `Garden`: Garden instances with location and metadata
- `GardenAccess`: User permissions per garden
- `Valve`: Individual valve control and status
- `Power`: Power management and monitoring
- `Pump`: Water pump control and status
- `Schedule`: Automated watering schedules
- `SystemLog`: Comprehensive event logging
- `WaterUsage`: Historical water consumption data
- `PowerConsumption`: Power usage tracking

**API Endpoints**:
```python
# Valve Management
GET    /api/garden/valves/                    # List all valves
POST   /api/garden/valves/{id}/control/       # Control valve (open/close)
POST   /api/garden/valves/{id}/set_duration/  # Set valve duration
GET    /api/garden/valves/status/             # Get all valve status

# System Control
POST   /api/garden/system/emergency_stop/     # Emergency stop all
POST   /api/garden/system/reset/              # Reset all systems
GET    /api/garden/system/status/             # Get system status

# Scheduling
GET    /api/garden/schedules/                 # List schedules
POST   /api/garden/schedules/                 # Create schedule
PUT    /api/garden/schedules/{id}/            # Update schedule
DELETE /api/garden/schedules/{id}/            # Delete schedule
POST   /api/garden/schedules/{id}/toggle/     # Toggle schedule

# Data & Analytics
GET    /api/garden/water-usage/by_period/     # Water usage data
GET    /api/garden/power-consumption/history/ # Power consumption
GET    /api/garden/logs/                      # System logs
```

#### 👤 Users App (`app/users/`)

**Custom User Model**:
```python
class User(AbstractUser):
    username = None  # Use email as username
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
```

**Authentication Features**:
- JWT token-based authentication
- Role-based permissions (Admin, Manager, Staff)
- Email-based login
- Password reset functionality

#### ⚙️ Tasks App (`app/tasks/`)

**Celery Background Tasks**:
```python
@shared_task
def execute_scheduled_watering(schedule_id):
    """Execute a scheduled watering task."""
    # Implementation for automated watering
    
@shared_task
def collect_sensor_data():
    """Collect data from ESP32 sensors via MQTT."""
    # Implementation for data collection
    
@shared_task
def system_health_check():
    """Perform system health monitoring."""
    # Implementation for health checks
```

### 🔄 Real-time Communication

**WebSocket Support**:
```python
# core/routing.py
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(URLRouter(ws_urlpatterns))
})
```

**MQTT Integration**:
- RabbitMQ with MQTT plugin for ESP32 communication
- Real-time sensor data ingestion
- Command publishing to IoT devices

### 🛡️ Security & Permissions

**Custom Permission Classes**:
```python
class IsGardenAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsGardenStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        return GardenAccess.objects.filter(
            user=request.user, 
            garden=obj.garden
        ).exists()
```

**Mock API Support**:
```python
def is_mock_mode(request):
    return request.query_params.get('use_mock', 'false').lower() == 'true'

class MockAwareViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        if is_mock_mode(self.request):
            return [AllowAny()]
        return super().get_permissions()
```

## 🏗️ Infrastructure

### 🐳 Docker Architecture

The system uses Docker Compose for orchestration with the following services:

#### 🔧 Core Services

**Django Application**:
```dockerfile
FROM python:3.10-alpine
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /src

# Install system dependencies for MySQL, Redis, etc.
RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev \
    libffi-dev jpeg-dev zlib-dev freetype-dev mariadb-dev

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Security: Create non-root user
RUN adduser -D user && chown -R user:user /src
USER user

ENTRYPOINT ["/entrypoint.sh"]
```

**Nginx Reverse Proxy**:
```nginx
server {
    listen 80;
    server_name haj-ebram.ir;
    
    # Frontend static files
    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API proxy
    location /api/ {
        proxy_pass http://app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    # RabbitMQ Management
    location /rabbit/ {
        proxy_pass http://broker:15672;
    }
}
```

#### 💾 Data Services

**MySQL Database**:
- Persistent data storage for application data
- User accounts, gardens, schedules, logs
- Optimized for transactional workloads

**Redis Cache**:
- Session storage and caching
- Celery message broker
- Real-time data caching

**InfluxDB Time Series**:
- Sensor data storage
- High-performance time-series queries
- Data retention policies

**RabbitMQ Message Broker**:
- MQTT broker for ESP32 communication
- Celery task queue
- Management interface on port 15672

### 🔄 Service Orchestration

**Main Docker Compose**:
```yaml
services:
  app:
    build: ./django_image/
    volumes:
      - ./app:/src
    ports:
      - 8000:8000
    depends_on:
      - db
      - redis
      - broker
    command: daphne -b 0.0.0.0 -p 8000 core.asgi:application

  nginx:
    extends:
      file: ./smart-garden-infra/docker-compose.yml
      service: nginx
    volumes:
      - ./smart-garden-front/out:/var/www/html
    ports:
      - "80:80"

  # Infrastructure services extended from submodule
  db:
    extends:
      file: ./smart-garden-infra/docker-compose.yml
      service: db
      
  redis:
    extends:
      file: ./smart-garden-infra/docker-compose.yml
      service: redis
```

### 🌐 Network Configuration

**Custom Bridge Network**:
```yaml
networks:
  custom_network:
    driver: bridge
    ipam:
      config:
        - subnet: 192.168.1.0/24
```

**Port Mapping**:
- `80`: Nginx (Web interface)
- `8000`: Django API (development)
- `3306`: MySQL database
- `6379`: Redis cache
- `5672`: RabbitMQ AMQP
- `15672`: RabbitMQ Management
- `8086`: InfluxDB
- `5555`: Flower (Celery monitoring)

## 🔄 Development Workflow

### 🛠️ Local Development

**Backend Development**:
```bash
# Start infrastructure services only
docker-compose up -d db redis broker influxdb

# Run Django locally with hot reload
cd app
python manage.py migrate
python manage.py runserver 8000

# Run Celery worker locally
celery -A core worker -l INFO

# Run Celery beat scheduler
celery -A core beat -l INFO
```

**Frontend Development**:
```bash
cd smart-garden-front
npm install
npm run dev  # Starts on http://localhost:3000
```

### 🔧 Database Management

**Migrations**:
```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

**Data Management**:
```bash
# Load initial data
python manage.py loaddata fixtures/initial_data.json

# Backup database
docker exec mysql mysqldump -u root -proot smart_garden > backup.sql

# Restore database
docker exec -i mysql mysql -u root -proot smart_garden < backup.sql
```

### 🧪 Testing & Quality

**Backend Testing**:
```bash
# Run Django tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

**Frontend Testing**:
```bash
# Run Jest tests
npm test

# Run E2E tests
npm run test:e2e

# Type checking
npm run type-check
```

**Code Quality**:
```bash
# Python linting
flake8 app/
black app/
isort app/

# JavaScript/TypeScript linting
npm run lint
npm run lint:fix
```

## 📊 Monitoring & Logging

### 📈 System Monitoring

**Django Prometheus Metrics**:
```python
# Automatic metrics collection
INSTALLED_APPS = [
    'django_prometheus',
    # ... other apps
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... other middleware
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]
```

**Celery Monitoring with Flower**:
```bash
# Access Flower dashboard
http://localhost:5555

# Monitor task execution, worker status, and performance
```

### 📝 Logging Configuration

**Django Logging**:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'smart_garden.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

**System Logs Model**:
```python
class SystemLog(models.Model):
    garden = models.ForeignKey(Garden, on_delete=models.CASCADE)
    event = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=20, choices=[
        ('Manual', 'Manual'),
        ('Automatic', 'Automatic'),
        ('System', 'System')
    ])
    level = models.CharField(max_length=10, choices=[
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error')
    ])
```

## 🔐 Security

### 🛡️ Authentication & Authorization

**JWT Token Authentication**:
```python
SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',),
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
```

**Role-based Access Control**:
```python
class GardenAccess(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),      # Full access
        ('manager', 'Manager'),  # Manage schedules and settings
        ('staff', 'Staff'),      # View and basic control
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    garden = models.ForeignKey(Garden, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
```

### 🔒 Security Headers & CORS

**CORS Configuration**:
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://185.252.86.186',
    'https://haj-ebram.ir',
]
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    'http://185.252.86.186',
    'https://haj-ebram.ir',
]
```

**Security Middleware**:
```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # ... other middleware
]
```

### 🔐 Data Protection

**Environment Variables**:
- Sensitive data stored in `.env` file
- Production secrets managed separately
- Database credentials isolated

**Input Validation**:
- Django REST Framework serializers
- Custom validation for IoT commands
- SQL injection prevention

## 🧪 Testing

### 🔬 Backend Testing

**Model Tests**:
```python
class GardenModelTest(TestCase):
    def test_garden_creation(self):
        garden = Garden.objects.create(
            name="Test Garden",
            description="A test garden"
        )
        self.assertEqual(garden.name, "Test Garden")
        self.assertTrue(garden.created_at)
```

**API Tests**:
```python
class ValveAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_valve_control(self):
        response = self.client.post('/api/garden/valves/1/control/', {
            'action': 'open',
            'duration': 300
        })
        self.assertEqual(response.status_code, 200)
```

### 🎭 Frontend Testing

**Component Tests**:
```typescript
import { render, screen } from '@testing-library/react'
import { ValveCard } from '@/components/valve-card'

test('renders valve card with correct status', () => {
  render(<ValveCard number={1} status="open" />)
  expect(screen.getByText('Valve 1')).toBeInTheDocument()
  expect(screen.getByText('Open')).toBeInTheDocument()
})
```

**Integration Tests**:
```typescript
import { getValveStatus } from '@/lib/api-client'

test('fetches valve status from API', async () => {
  const valves = await getValveStatus()
  expect(Array.isArray(valves)).toBe(true)
  expect(valves[0]).toHaveProperty('id')
  expect(valves[0]).toHaveProperty('status')
})
```

## 📚 API Documentation

### 🔍 Interactive Documentation

The API provides comprehensive documentation through multiple interfaces:

- **Swagger UI**: http://localhost/api/docs/
- **ReDoc**: http://localhost/api/schema/redoc/
- **OpenAPI Schema**: http://localhost/api/schema/

### 📋 Core API Endpoints

**Authentication**:
```http
POST /api/users/auth/jwt/create/     # Login
POST /api/users/auth/jwt/refresh/    # Refresh token
POST /api/users/auth/jwt/verify/     # Verify token
POST /api/users/auth/users/          # Register
```

**Garden Management**:
```http
GET    /api/garden/valves/           # List valves
POST   /api/garden/valves/{id}/control/  # Control valve
GET    /api/garden/system/status/    # System status
POST   /api/garden/system/emergency_stop/  # Emergency stop
```

**Data & Analytics**:
```http
GET /api/garden/water-usage/by_period/?period=daily&startDate=2024-01-01&endDate=2024-01-31
GET /api/garden/power-consumption/history/?period=weekly
GET /api/garden/logs/?source=Automatic&startDate=2024-01-01
```

### 📝 Request/Response Examples

**Valve Control**:
```json
// POST /api/garden/valves/1/control/
{
  "action": "open",
  "duration": 300,
  "source": "Manual"
}

// Response
{
  "success": true,
  "valve": {
    "id": 1,
    "number": 1,
    "status": "on",
    "duration": 300,
    "last_active": "2024-01-15T10:30:00Z"
  }
}
```

**Schedule Creation**:
```json
// POST /api/garden/schedules/
{
  "startTime": "08:00 AM",
  "duration": "30 minutes",
  "target": "Valve 1",
  "repeat": "Daily",
  "days": ["monday", "wednesday", "friday"],
  "isActive": true
}
```

## 🤝 Contributing

### 🔄 Development Process

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/new-feature
   ```
3. **Make changes and test**:
   ```bash
   # Backend tests
   python manage.py test
   
   # Frontend tests
   npm test
   ```
4. **Commit with conventional commits**:
   ```bash
   git commit -m "feat: add valve scheduling feature"
   ```
5. **Push and create Pull Request**

### 📋 Code Standards

**Python (Backend)**:
- Follow PEP 8 style guide
- Use Black for code formatting
- Type hints where applicable
- Comprehensive docstrings

**TypeScript (Frontend)**:
- Follow ESLint configuration
- Use Prettier for formatting
- Strict TypeScript mode
- Component documentation

**Git Workflow**:
- Conventional commit messages
- Feature branches from main
- Squash commits before merge
- Update documentation

### 🐛 Bug Reports

When reporting bugs, please include:
- Environment details (OS, Docker version)
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs and screenshots
- Configuration details

### 💡 Feature Requests

For new features, please provide:
- Clear use case description
- Proposed implementation approach
- Impact on existing functionality
- Documentation requirements

---

## 📞 Support & Contact

- **Repository**: https://github.com/HosseinlGholami/smart-garden-backend
- **Frontend Submodule**: https://github.com/HosseinlGholami/smart-garden-front
- **Infrastructure Submodule**: https://github.com/HosseinlGholami/smart-garden-infra
- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Documentation**: This README and inline code documentation

---

**Built with ❤️ for smart agriculture and IoT automation**
