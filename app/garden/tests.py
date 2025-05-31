"""
Comprehensive tests for the garden app.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta
import json

from .models import (
    Garden, GardenAccess, Valve, Power, Pump, Schedule, 
    SystemLog, WaterUsage, PowerConsumption
)
from .serializers import (
    GardenSerializer, ValveSerializer, PowerSerializer, 
    PumpSerializer, ScheduleSerializer, SystemLogSerializer
)
from .permissions import IsGardenAdmin, IsGardenManager, IsGardenStaff

User = get_user_model()


class GardenModelTest(TestCase):
    """Test cases for Garden model."""
    
    def setUp(self):
        from .models import Garden
        
        self.garden = Garden.objects.create(
            name="Test Garden",
            description="A beautiful test garden",
            location="Test Location"
        )
    
    def test_garden_creation(self):
        """Test garden creation with required fields."""
        self.assertEqual(self.garden.name, "Test Garden")
        self.assertEqual(self.garden.description, "A beautiful test garden")
        self.assertEqual(self.garden.location, "Test Location")
        self.assertTrue(self.garden.created_at)
        self.assertTrue(self.garden.updated_at)
    
    def test_garden_str_method(self):
        """Test garden string representation."""
        self.assertEqual(str(self.garden), "Test Garden")
    
    def test_garden_update_timestamp(self):
        """Test that updated_at changes when garden is modified."""
        original_updated_at = self.garden.updated_at
        self.garden.description = "Updated description"
        self.garden.save()
        self.assertNotEqual(self.garden.updated_at, original_updated_at)


class GardenAccessModelTest(TestCase):
    """Test cases for GardenAccess model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.garden = Garden.objects.create(
            name="Test Garden",
            description="Test garden for access control"
        )
        self.garden_access = GardenAccess.objects.create(
            user=self.user,
            garden=self.garden,
            role='admin'
        )
    
    def test_garden_access_creation(self):
        """Test garden access creation."""
        self.assertEqual(self.garden_access.user, self.user)
        self.assertEqual(self.garden_access.garden, self.garden)
        self.assertEqual(self.garden_access.role, 'admin')
    
    def test_garden_access_unique_constraint(self):
        """Test that user-garden combination is unique."""
        with self.assertRaises(Exception):
            GardenAccess.objects.create(
                user=self.user,
                garden=self.garden,
                role='staff'
            )
    
    def test_garden_access_str_method(self):
        """Test garden access string representation."""
        expected_str = f"{self.user} - {self.garden} (admin)"
        self.assertEqual(str(self.garden_access), expected_str)


class ValveModelTest(TestCase):
    """Test cases for Valve model."""
    
    def setUp(self):
        self.garden = Garden.objects.create(name="Test Garden")
        self.valve = Valve.objects.create(
            garden=self.garden,
            number=1,
            status='off',
            duration=300
        )
    
    def test_valve_creation(self):
        """Test valve creation with default values."""
        self.assertEqual(self.valve.garden, self.garden)
        self.assertEqual(self.valve.number, 1)
        self.assertEqual(self.valve.status, 'off')
        self.assertEqual(self.valve.duration, 300)
        self.assertIsNone(self.valve.last_active)
    
    def test_valve_activation(self):
        """Test valve activation."""
        self.valve.status = 'on'
        self.valve.last_active = timezone.now()
        self.valve.save()
        
        self.assertEqual(self.valve.status, 'on')
        self.assertIsNotNone(self.valve.last_active)
    
    def test_valve_unique_constraint(self):
        """Test that garden-number combination is unique."""
        with self.assertRaises(Exception):
            Valve.objects.create(
                garden=self.garden,
                number=1,  # Same number as existing valve
                status='off'
            )


class PowerModelTest(TestCase):
    """Test cases for Power model."""
    
    def setUp(self):
        self.garden = Garden.objects.create(name="Test Garden")
        self.power = Power.objects.create(
            garden=self.garden,
            status='on'
        )
    
    def test_power_creation(self):
        """Test power model creation."""
        self.assertEqual(self.power.garden, self.garden)
        self.assertEqual(self.power.status, 'on')
        self.assertTrue(self.power.last_status_change)


class ScheduleModelTest(TestCase):
    """Test cases for Schedule model."""
    
    def setUp(self):
        self.garden = Garden.objects.create(name="Test Garden")
        self.schedule = Schedule.objects.create(
            garden=self.garden,
            startTime="08:00 AM",
            duration="30 minutes",
            target="Valve 1",
            repeat="Daily",
            isActive=True
        )
    
    def test_schedule_creation(self):
        """Test schedule creation."""
        self.assertEqual(self.schedule.garden, self.garden)
        self.assertEqual(self.schedule.startTime, "08:00 AM")
        self.assertEqual(self.schedule.duration, "30 minutes")
        self.assertEqual(self.schedule.target, "Valve 1")
        self.assertEqual(self.schedule.repeat, "Daily")
        self.assertTrue(self.schedule.isActive)
    
    def test_schedule_with_weekly_days(self):
        """Test schedule with weekly repeat and specific days."""
        weekly_schedule = Schedule.objects.create(
            garden=self.garden,
            startTime="06:00 PM",
            duration="20 minutes",
            target="Valve 2",
            repeat="Weekly",
            days=["monday", "wednesday", "friday"],
            isActive=True
        )
        
        self.assertEqual(weekly_schedule.repeat, "Weekly")
        self.assertEqual(weekly_schedule.days, ["monday", "wednesday", "friday"])


class SystemLogModelTest(TestCase):
    """Test cases for SystemLog model."""
    
    def setUp(self):
        self.garden = Garden.objects.create(name="Test Garden")
        self.log = SystemLog.objects.create(
            garden=self.garden,
            event="Valve 1 opened",
            source="Manual"
        )
    
    def test_system_log_creation(self):
        """Test system log creation."""
        self.assertEqual(self.log.garden, self.garden)
        self.assertEqual(self.log.event, "Valve 1 opened")
        self.assertEqual(self.log.source, "Manual")
        self.assertTrue(self.log.timestamp)


class GardenSerializerTest(TestCase):
    """Test cases for Garden serializer."""
    
    def setUp(self):
        self.garden_data = {
            'name': 'Test Garden',
            'description': 'Test description',
            'location': 'Test Location'
        }
        self.garden = Garden.objects.create(**self.garden_data)
    
    def test_garden_serialization(self):
        """Test garden serialization."""
        serializer = GardenSerializer(self.garden)
        self.assertEqual(serializer.data['name'], self.garden_data['name'])
        self.assertEqual(serializer.data['description'], self.garden_data['description'])
        self.assertEqual(serializer.data['location'], self.garden_data['location'])
    
    def test_garden_deserialization(self):
        """Test garden deserialization."""
        serializer = GardenSerializer(data=self.garden_data)
        self.assertTrue(serializer.is_valid())
        garden = serializer.save()
        self.assertEqual(garden.name, self.garden_data['name'])


class ValveAPITest(APITestCase):
    """Test cases for Valve API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role='admin'
        )
        self.garden = Garden.objects.create(name="Test Garden")
        self.garden_access = GardenAccess.objects.create(
            user=self.user,
            garden=self.garden,
            role='admin'
        )
        self.valve = Valve.objects.create(
            garden=self.garden,
            number=1,
            status='off',
            duration=300
        )
        
        # Set up JWT authentication
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {refresh.access_token}')
    
    def test_valve_list(self):
        """Test retrieving valve list."""
        url = reverse('valve-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_valve_control_open(self):
        """Test opening a valve."""
        url = reverse('valve-control', kwargs={'pk': self.valve.pk})
        data = {
            'action': 'open',
            'duration': 600,
            'source': 'Manual'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify valve was updated
        self.valve.refresh_from_db()
        self.assertEqual(self.valve.status, 'on')
        self.assertEqual(self.valve.duration, 600)
    
    def test_valve_control_close(self):
        """Test closing a valve."""
        # First open the valve
        self.valve.status = 'on'
        self.valve.save()
        
        url = reverse('valve-control', kwargs={'pk': self.valve.pk})
        data = {
            'action': 'close',
            'source': 'Manual'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify valve was closed
        self.valve.refresh_from_db()
        self.assertEqual(self.valve.status, 'off')
    
    def test_valve_control_invalid_action(self):
        """Test valve control with invalid action."""
        url = reverse('valve-control', kwargs={'pk': self.valve.pk})
        data = {
            'action': 'invalid_action',
            'source': 'Manual'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_valve_status(self):
        """Test getting valve status."""
        url = reverse('valve-status')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_valve_set_duration(self):
        """Test setting valve duration."""
        url = reverse('valve-set-duration', kwargs={'pk': self.valve.pk})
        data = {'duration': 900}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify duration was updated
        self.valve.refresh_from_db()
        self.assertEqual(self.valve.duration, 900)


class MockAPITest(APITestCase):
    """Test cases for mock API functionality."""
    
    def test_valve_status_with_mock(self):
        """Test valve status endpoint with mock mode."""
        url = reverse('valve-status') + '?use_mock=true'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Mock mode should bypass authentication
    
    def test_system_status_with_mock(self):
        """Test system status endpoint with mock mode."""
        url = reverse('system-status') + '?use_mock=true'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SystemControlAPITest(APITestCase):
    """Test cases for system control API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            role='admin'
        )
        self.garden = Garden.objects.create(name="Test Garden")
        self.garden_access = GardenAccess.objects.create(
            user=self.user,
            garden=self.garden,
            role='admin'
        )
        
        # Create test valves
        for i in range(1, 4):
            Valve.objects.create(
                garden=self.garden,
                number=i,
                status='on'  # Start with valves open
            )
        
        # Set up authentication
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {refresh.access_token}')
    
    def test_emergency_stop(self):
        """Test emergency stop functionality."""
        url = reverse('system-emergency-stop')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify all valves are closed
        valves = Valve.objects.filter(garden=self.garden)
        for valve in valves:
            self.assertEqual(valve.status, 'off')
    
    def test_system_reset(self):
        """Test system reset functionality."""
        url = reverse('system-reset')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_system_status(self):
        """Test system status endpoint."""
        url = reverse('system-status')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify response structure
        self.assertIn('isConnected', response.data)
        self.assertIn('nextSchedule', response.data)
        self.assertIn('lastChecked', response.data)


class ScheduleAPITest(APITestCase):
    """Test cases for Schedule API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='manager@example.com',
            password='managerpass123',
            role='manager'
        )
        self.garden = Garden.objects.create(name="Test Garden")
        self.garden_access = GardenAccess.objects.create(
            user=self.user,
            garden=self.garden,
            role='manager'
        )
        
        self.schedule_data = {
            'garden': self.garden.id,
            'startTime': '08:00 AM',
            'duration': '30 minutes',
            'target': 'Valve 1',
            'repeat': 'Daily',
            'isActive': True
        }
        
        # Set up authentication
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {refresh.access_token}')
    
    def test_create_schedule(self):
        """Test creating a new schedule."""
        url = reverse('schedule-list')
        response = self.client.post(url, self.schedule_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify schedule was created
        schedule = Schedule.objects.get(id=response.data['id'])
        self.assertEqual(schedule.startTime, self.schedule_data['startTime'])
        self.assertEqual(schedule.target, self.schedule_data['target'])
    
    def test_schedule_toggle(self):
        """Test toggling schedule active status."""
        schedule = Schedule.objects.create(**self.schedule_data)
        url = reverse('schedule-toggle', kwargs={'pk': schedule.pk})
        
        original_status = schedule.isActive
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify status was toggled
        schedule.refresh_from_db()
        self.assertNotEqual(schedule.isActive, original_status)
    
    def test_weekly_schedule_with_days(self):
        """Test creating weekly schedule with specific days."""
        weekly_data = self.schedule_data.copy()
        weekly_data.update({
            'repeat': 'Weekly',
            'days': ['monday', 'wednesday', 'friday']
        })
        
        url = reverse('schedule-list')
        response = self.client.post(url, weekly_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        schedule = Schedule.objects.get(id=response.data['id'])
        self.assertEqual(schedule.repeat, 'Weekly')
        self.assertEqual(schedule.days, ['monday', 'wednesday', 'friday'])


class PermissionTest(APITestCase):
    """Test cases for permission system."""
    
    def setUp(self):
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            role='admin'
        )
        self.manager_user = User.objects.create_user(
            email='manager@example.com',
            password='managerpass123',
            role='manager'
        )
        self.staff_user = User.objects.create_user(
            email='staff@example.com',
            password='staffpass123',
            role='staff'
        )
        
        self.garden = Garden.objects.create(name="Test Garden")
        
        # Create garden access for each user
        GardenAccess.objects.create(
            user=self.admin_user,
            garden=self.garden,
            role='admin'
        )
        GardenAccess.objects.create(
            user=self.manager_user,
            garden=self.garden,
            role='manager'
        )
        GardenAccess.objects.create(
            user=self.staff_user,
            garden=self.garden,
            role='staff'
        )
    
    def _authenticate_user(self, user):
        """Helper method to authenticate a user."""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {refresh.access_token}')
    
    def test_admin_can_access_all(self):
        """Test that admin users can access all endpoints."""
        self._authenticate_user(self.admin_user)
        
        # Test garden list access
        url = reverse('garden-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_staff_can_view_valves(self):
        """Test that staff users can view valves."""
        self._authenticate_user(self.staff_user)
        
        url = reverse('valve-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users are denied access."""
        url = reverse('valve-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_garden_filtering_by_access(self):
        """Test that users only see gardens they have access to."""
        # Create another garden without access for test user
        other_garden = Garden.objects.create(name="Other Garden")
        
        self._authenticate_user(self.staff_user)
        url = reverse('garden-list')
        response = self.client.get(url)
        
        # Should only see the garden they have access to
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test Garden")


class DataAnalyticsTest(APITestCase):
    """Test cases for data analytics endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='analyst@example.com',
            password='analystpass123',
            role='manager'
        )
        self.garden = Garden.objects.create(name="Analytics Garden")
        GardenAccess.objects.create(
            user=self.user,
            garden=self.garden,
            role='manager'
        )
        
        # Create test data
        for i in range(7):  # 7 days of data
            date = timezone.now().date() - timedelta(days=i)
            WaterUsage.objects.create(
                garden=self.garden,
                period=f"Day {i+1}",
                valve1=10.0 + i,
                valve2=8.0 + i,
                valve3=6.0 + i
            )
            
            PowerConsumption.objects.create(
                garden=self.garden,
                time=f"{8+i}:00",
                consumption=45.0 + i,
                date=date
            )
        
        # Set up authentication
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {refresh.access_token}')
    
    def test_water_usage_by_period(self):
        """Test water usage analytics endpoint."""
        url = reverse('waterusage-by-period')
        response = self.client.get(url, {'period': 'weekly'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_power_consumption_history(self):
        """Test power consumption history endpoint."""
        url = reverse('powerconsumption-history')
        response = self.client.get(url, {'period': 'daily'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_system_logs_filtering(self):
        """Test system logs with filtering."""
        # Create test logs
        SystemLog.objects.create(
            garden=self.garden,
            event="Test manual event",
            source="Manual"
        )
        SystemLog.objects.create(
            garden=self.garden,
            event="Test automatic event",
            source="Automatic"
        )
        
        url = reverse('systemlog-list')
        response = self.client.get(url, {'source': 'Manual'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only return manual logs
        manual_logs = [log for log in response.data if log['source'] == 'Manual']
        self.assertEqual(len(manual_logs), 1)


class ErrorHandlingTest(APITestCase):
    """Test cases for error handling."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='error@example.com',
            password='errorpass123'
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {refresh.access_token}')
    
    def test_nonexistent_valve_control(self):
        """Test controlling non-existent valve returns 404."""
        url = reverse('valve-control', kwargs={'pk': 999})
        data = {'action': 'open'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_invalid_schedule_data(self):
        """Test creating schedule with invalid data."""
        url = reverse('schedule-list')
        invalid_data = {
            'startTime': '',  # Invalid empty time
            'duration': '',   # Invalid empty duration
            'target': '',     # Invalid empty target
            'repeat': 'InvalidRepeat'  # Invalid repeat option
        }
        response = self.client.post(url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 