this is my project which has two submodules, one of them is smart-garden-front
and the other one is smart-garden-infa and i do have based project which is my django.


# 🌿 Smart Garden Watering Automation

A smart irrigation system using ESP32, MQTT, Django, and React. Control your garden's watering remotely, view real-time status, and schedule automatic watering — all from your phone or PC.

## 🚀 Features

- Real-time dashboard (valves, pump, power status)
- Manual control via web or physical buttons
- Scheduled watering with background jobs
- MQTT communication (ESP32 ↔ Server)
- Mobile-friendly web interface
- Data visualization with charts
- Celery task scheduling for automated watering

## 🏗️ Architecture

### Backend (Django)
- Django REST Framework for API
- Django Channels for WebSockets
- Celery for task scheduling and background jobs
- MySQL for persistent data storage
- Redis for caching and message broker
- InfluxDB for time-series data
- RabbitMQ for MQTT broker

### Frontend (Next.js)
- Next.js 15 React framework
- Tailwind CSS for styling
- shadcn/ui component library
- Chart.js for data visualization
- Mobile-responsive design

### Infrastructure
- Docker and Docker Compose for containerization
- Nginx for web server and reverse proxy
- Monitoring with Prometheus metrics

## 📂 Repository Structure

This repository contains three main components:

1. **Backend**: Django application in `/app` directory
2. **Frontend**: Next.js application in `/smart-garden-front` submodule
3. **Infrastructure**: Docker configurations in `/smart-garden-infra` submodule

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Git

### Setup Instructions

1. Clone the repository with submodules:
   ```
   git clone --recurse-submodules https://github.com/HosseinlGholami/smart-garden-backend.git
   ```

2. If you've already cloned the repository without submodules:
   ```
   git submodule update --init --recursive
   ```

3. Create a `.env` file in the root directory with required environment variables

4. Build and start the containers:
   ```
   docker-compose up -d
   ```

5. Access the application:
   - Web UI: http://localhost
   - Admin panel: http://localhost/admin
   - API documentation: http://localhost/api/schema/swagger-ui/
   - Celery monitoring: http://localhost:5555

## 📱 ESP32 Integration

The system integrates with ESP32 microcontrollers through MQTT protocol. ESP32 devices connect to the RabbitMQ broker to:
- Send sensor data (moisture, temperature)
- Receive control commands (valve operation, pump control)
- Report device status

## 👨‍💻 Development

For local development:

1. Start the backend:
   ```
   docker-compose up -d
   ```

2. Start the frontend development server:
   ```
   cd smart-garden-front
   npm install
   npm run dev
   ```
