from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views import (
    GardenViewSet, GardenAccessViewSet,
    ValveViewSet, PowerViewSet, PumpViewSet, SystemLogViewSet,
    ScheduleViewSet, WaterUsageViewSet, PowerConsumptionViewSet,
    SystemControlViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()

# Register Garden management endpoints
router.register(r'gardens', GardenViewSet)
router.register(r'garden-access', GardenAccessViewSet)

# Register API endpoints for Smart Garden System
router.register(r'valves', ValveViewSet)
router.register(r'power', PowerViewSet)
router.register(r'pump', PumpViewSet)
router.register(r'logs', SystemLogViewSet)
router.register(r'schedules', ScheduleViewSet)
router.register(r'water-usage', WaterUsageViewSet)
router.register(r'power-consumption', PowerConsumptionViewSet)
router.register(r'system', SystemControlViewSet, basename='system')

urlpatterns = [
    path('', include(router.urls)),
    
    # API Documentation specific to garden app
    path('schema/', SpectacularAPIView.as_view(), name='garden-schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='garden-schema'), name='garden-swagger-ui'),
] 