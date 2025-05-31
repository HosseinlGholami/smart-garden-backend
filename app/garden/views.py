from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from datetime import datetime
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from .models import (
    Garden, GardenAccess, Valve, Power, Pump, Schedule, SystemLog,
    WaterUsage, PowerConsumption
)
from .serializers import (
    GardenSerializer, GardenAccessSerializer,
    ValveSerializer, PowerSerializer, PumpSerializer,
    SystemLogSerializer, ScheduleSerializer,
    WaterUsageSerializer, PowerConsumptionSerializer,
    SystemStatusSerializer
)
from .permissions import IsGardenAdmin, IsGardenManager, IsGardenStaff


# Add this function to check for mock mode
def is_mock_mode(request):
    """Check if request is in mock mode (use_mock=true)."""
    return request.query_params.get('use_mock', 'false').lower() == 'true'


# Base ViewSet for mock-aware authentication
class MockAwareViewSet(viewsets.ModelViewSet):
    """Base ViewSet that allows mock mode without authentication."""
    
    def get_permissions(self):
        """
        Override to bypass authentication when in mock mode.
        """
        if is_mock_mode(self.request):
            return [AllowAny()]
        return super().get_permissions()


class GardenViewSet(MockAwareViewSet):
    """API endpoint for gardens."""
    queryset = Garden.objects.all()
    serializer_class = GardenSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter gardens based on user access."""
        user = self.request.user
        
        # Superusers can see all gardens
        if user.is_superuser:
            return Garden.objects.all()
            
        # Regular users can only see gardens they have access to
        return Garden.objects.filter(user_accesses__user=user).distinct()


class GardenAccessViewSet(MockAwareViewSet):
    """API endpoint for managing garden access."""
    queryset = GardenAccess.objects.all()
    serializer_class = GardenAccessSerializer
    permission_classes = [IsAuthenticated, IsGardenAdmin]
    
    def get_queryset(self):
        """Filter garden access based on user's gardens."""
        user = self.request.user
        
        # Superusers can see all garden accesses
        if user.is_superuser:
            return GardenAccess.objects.all()
            
        # Garden admins can see accesses for gardens they administer
        admin_gardens = Garden.objects.filter(
            user_accesses__user=user,
            user_accesses__role='admin'
        )
        
        return GardenAccess.objects.filter(garden__in=admin_gardens)


# Smart Garden System ViewSets
class ValveViewSet(MockAwareViewSet):
    """API endpoint for valves."""
    queryset = Valve.objects.all()
    serializer_class = ValveSerializer
    permission_classes = [IsAuthenticated, IsGardenStaff]
    
    def get_queryset(self):
        """Filter valves based on user garden access."""
        user = self.request.user
        
        # Superusers can see all valves
        if user.is_superuser:
            return Valve.objects.all()
            
        # Filter by garden_id if provided in query params
        garden_id = self.request.query_params.get('garden_id')
        if garden_id:
            if GardenAccess.objects.filter(user=user, garden_id=garden_id).exists():
                return Valve.objects.filter(garden_id=garden_id)
            return Valve.objects.none()
            
        # Otherwise, return valves from all accessible gardens
        accessible_gardens = Garden.objects.filter(user_accesses__user=user)
        return Valve.objects.filter(garden__in=accessible_gardens)
    
    @extend_schema(
        summary="Control a valve",
        description="Opens or closes a specific valve and optionally sets its duration",
        request={"application/json": {"example": {"action": "open", "duration": 300, "source": "Manual"}}},
        responses={200: {"example": {"success": True, "valve": {"id": 1, "number": 1, "status": "on", "duration": 300}}}}
    )
    @action(detail=True, methods=['post'])
    def control(self, request, pk=None):
        """Control a valve (open/close)."""
        valve = self.get_object()
        action = request.data.get('action', '')
        duration = request.data.get('duration', valve.duration)
        
        if action == 'open':
            valve.status = 'on'
            valve.duration = duration
            valve.last_active = timezone.now()
            valve.save()
            
            # Log the event
            SystemLog.objects.create(
                garden=valve.garden,
                event=f"Valve {valve.number} turned on",
                source=request.data.get('source', 'Manual')
            )
            
            return Response({
                'success': True,
                'valve': ValveSerializer(valve).data
            })
        elif action == 'close':
            valve.status = 'off'
            valve.save()
            
            # Log the event
            SystemLog.objects.create(
                garden=valve.garden,
                event=f"Valve {valve.number} turned off",
                source=request.data.get('source', 'Manual')
            )
            
            return Response({
                'success': True,
                'valve': ValveSerializer(valve).data
            })
        else:
            return Response(
                {'error': 'Invalid action. Use "open" or "close".'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        summary="Set valve duration",
        description="Set the duration in seconds for a specific valve",
        request={"application/json": {"example": {"duration": 600}}},
        responses={200: {"example": {"success": True, "valve": {"id": 1, "number": 1, "status": "off", "duration": 600}}}}
    )
    @action(detail=True, methods=['post'])
    def set_duration(self, request, pk=None):
        """Set the duration for a valve."""
        valve = self.get_object()
        duration = request.data.get('duration')
        
        if duration is not None:
            valve.duration = int(duration)
            valve.save()
            return Response({
                'success': True,
                'valve': ValveSerializer(valve).data
            })
        else:
            return Response(
                {'error': 'Duration is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name="garden_id", description="Filter by garden ID", required=False, type=int)
        ],
        summary="Get all valves status",
        description="Returns the status of all valves in the system",
        responses={200: {"example": [{"id": 1, "number": 1, "status": "off", "duration": 300}]}}
    )
    @action(detail=False)
    def status(self, request):
        """Get status of all valves."""
        valves = self.get_queryset()
        serializer = ValveSerializer(valves, many=True)
        return Response(serializer.data)


class PowerViewSet(MockAwareViewSet):
    """API endpoint for power management."""
    queryset = Power.objects.all()
    serializer_class = PowerSerializer
    
    @extend_schema(
        summary="Get power status",
        description="Returns the current power status (on/off)",
        responses={200: {"example": {"status": "on"}}}
    )
    @action(detail=False)
    def status(self, request):
        """Get the current power status."""
        power = Power.objects.first()
        if not power:
            power = Power.objects.create(status='on')
        
        return Response({'status': power.status})


class PumpViewSet(MockAwareViewSet):
    """API endpoint for pump control."""
    queryset = Pump.objects.all()
    serializer_class = PumpSerializer
    
    @extend_schema(
        summary="Get pump status",
        description="Returns the current pump status (on/off)",
        responses={200: {"example": {"status": "off"}}}
    )
    @action(detail=False)
    def status(self, request):
        """Get the current pump status."""
        pump = Pump.objects.first()
        if not pump:
            pump = Pump.objects.create(status='off')
        
        return Response({'status': pump.status})
    
    @extend_schema(
        summary="Control pump",
        description="Start or stop the water pump",
        request={"application/json": {"example": {"action": "start", "source": "Manual"}}},
        responses={200: {"example": {"success": True, "pump": {"status": "on"}}}}
    )
    @action(detail=False, methods=['post'])
    def control(self, request):
        """Control the pump (start/stop)."""
        pump = Pump.objects.first()
        if not pump:
            pump = Pump.objects.create(status='off')
        
        action = request.data.get('action', '')
        
        if action == 'start':
            pump.status = 'on'
            pump.save()
            
            # Log the event
            SystemLog.objects.create(
                event="Pump started",
                source=request.data.get('source', 'Manual')
            )
            
            return Response({
                'success': True,
                'pump': {'status': pump.status}
            })
        elif action == 'stop':
            pump.status = 'off'
            pump.save()
            
            # Log the event
            SystemLog.objects.create(
                event="Pump stopped",
                source=request.data.get('source', 'Manual')
            )
            
            return Response({
                'success': True,
                'pump': {'status': pump.status}
            })
        else:
            return Response(
                {'error': 'Invalid action. Use "start" or "stop".'},
                status=status.HTTP_400_BAD_REQUEST
            )


class SystemLogViewSet(MockAwareViewSet):
    """API endpoint for system logs."""
    queryset = SystemLog.objects.all()
    serializer_class = SystemLogSerializer
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name="source", description="Filter logs by source (Manual/Automatic/System)", required=False, type=str)
        ],
        summary="Get system logs",
        description="Returns system logs, optionally filtered by source"
    )
    def get_queryset(self):
        """Filter logs based on query parameters."""
        queryset = SystemLog.objects.all()
        source = self.request.query_params.get('source', None)
        
        if source:
            queryset = queryset.filter(source=source)
        
        return queryset


class ScheduleViewSet(MockAwareViewSet):
    """API endpoint for watering schedules."""
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    
    @extend_schema(
        summary="Toggle schedule",
        description="Toggle a schedule between active and inactive states",
        responses={200: {"example": {"success": True, "schedule": {
            "id": 1, 
            "startTime": "08:00 AM",
            "duration": "30 minutes",
            "target": "Valve 1",
            "repeat": "Daily",
            "isActive": False
        }}}}
    )
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Toggle a schedule active/inactive."""
        schedule = self.get_object()
        schedule.isActive = not schedule.isActive
        schedule.save()
        
        return Response({
            'success': True,
            'schedule': ScheduleSerializer(schedule).data
        })


class WaterUsageViewSet(MockAwareViewSet):
    """API endpoint for water usage data."""
    queryset = WaterUsage.objects.all()
    serializer_class = WaterUsageSerializer
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name="period", description="Time period (week/month/year)", required=False, type=str),
            OpenApiParameter(name="startDate", description="Start date (YYYY-MM-DD)", required=False, type=str),
            OpenApiParameter(name="endDate", description="End date (YYYY-MM-DD)", required=False, type=str)
        ],
        summary="Get water usage by period",
        description="Returns water usage data filtered by time period and date range"
    )
    @action(detail=False)
    def by_period(self, request):
        """Get water usage data by time period."""
        period = request.query_params.get('period', 'week')
        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')
        
        # Filter by date range if provided
        queryset = self.get_queryset()
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(timestamp__date__gte=start, timestamp__date__lte=end)
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Limit results based on period
        if period == 'week':
            queryset = queryset.order_by('-timestamp')[:7]
        elif period == 'month':
            queryset = queryset.order_by('-timestamp')[:30]
        elif period == 'year':
            queryset = queryset.order_by('-timestamp')[:365]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PowerConsumptionViewSet(MockAwareViewSet):
    """API endpoint for power consumption data."""
    queryset = PowerConsumption.objects.all()
    serializer_class = PowerConsumptionSerializer
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name="period", description="Time period (day/week/month)", required=False, type=str),
            OpenApiParameter(name="startDate", description="Start date (YYYY-MM-DD)", required=False, type=str),
            OpenApiParameter(name="endDate", description="End date (YYYY-MM-DD)", required=False, type=str)
        ],
        summary="Get power consumption history",
        description="Returns power consumption data filtered by time period and date range"
    )
    @action(detail=False)
    def history(self, request):
        """Get power consumption history filtered by period and date range."""
        period = request.query_params.get('period', 'day')
        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')
        
        # Filter by date range if provided
        queryset = self.get_queryset()
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=start, date__lte=end)
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Group or limit results based on period
        if period == 'day':
            # Today's data with hourly samples
            queryset = queryset.filter(date=timezone.now().date()).order_by('time')
        elif period == 'week':
            # Last 7 days aggregated data
            queryset = queryset.order_by('-date')[:7]
        elif period == 'month':
            # Last 30 days aggregated data
            queryset = queryset.order_by('-date')[:30]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SystemControlViewSet(MockAwareViewSet):
    """API endpoint for system-wide controls and status."""
    permission_classes = [IsAuthenticated]
    basename = 'system'
    
    @extend_schema(
        summary="Emergency stop",
        description="Immediately stop all valves and pump",
        responses={200: {"example": {"success": True}}}
    )
    @action(detail=False, methods=['post'])
    def emergency_stop(self, request):
        """Emergency stop for all valves and pump."""
        # Turn off all valves
        valves = Valve.objects.all()
        for valve in valves:
            valve.status = 'off'
            valve.save()
        
        # Turn off pump
        pump = Pump.objects.first()
        if pump:
            pump.status = 'off'
            pump.save()
        
        # Log the event
        SystemLog.objects.create(
            event="Emergency stop activated",
            source="Manual"
        )
        
        return Response({'success': True})
    
    @extend_schema(
        summary="Reset system",
        description="Reset all systems for troubleshooting",
        responses={200: {"example": {"success": True}}}
    )
    @action(detail=False, methods=['post'])
    def reset(self, request):
        """Reset all systems (for troubleshooting)."""
        # Reset power
        power = Power.objects.first()
        if power:
            power.status = 'on'
            power.save()
        
        # Log the event
        SystemLog.objects.create(
            event="System reset performed",
            source="Manual"
        )
        
        return Response({'success': True})
    
    @extend_schema(
        summary="Get system status",
        description="Returns the overall system status including connection and next scheduled event",
        responses={200: {"example": {
            "isConnected": True,
            "nextSchedule": {"time": "8:00 AM", "target": "Valve 1"},
            "lastChecked": "2023-08-10T12:00:00Z"
        }}}
    )
    @action(detail=False)
    def status(self, request):
        """Get the overall system status."""
        # Check if any valve is active
        active_valves = Valve.objects.filter(status='on').exists()
        
        # Get next scheduled event
        next_schedule = Schedule.objects.filter(isActive=True).first()
        next_schedule_data = {}
        
        if next_schedule:
            next_schedule_data = {
                'time': next_schedule.startTime,
                'target': next_schedule.target
            }
        else:
            next_schedule_data = {
                'time': 'No upcoming schedules',
                'target': 'None'
            }
        
        # Simulate active connection
        is_connected = True
        
        return Response({
            'isConnected': is_connected,
            'nextSchedule': next_schedule_data,
            'lastChecked': timezone.now()
        })
    
    @extend_schema(
        summary="Toggle mock API mode",
        description="Enable or disable mock API mode for testing",
        request={"application/json": {"example": {"use_mock": True}}},
        responses={200: {"example": {"success": True, "use_mock_api": True, "message": "Mock API mode enabled"}}}
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def mock_api_toggle(self, request):
        """Toggle mock API mode for testing and development."""
        # This is a server-side setting that could influence how the frontend behaves
        # For example, you could store this in a database setting
        use_mock = request.data.get('use_mock', False)
        
        # You could save this setting to the database if needed
        
        return Response({
            'success': True,
            'use_mock_api': use_mock,
            'message': f"Mock API mode {'enabled' if use_mock else 'disabled'}"
        })
    
    def get_queryset(self):
        """For ViewSet compatibility."""
        return [] 