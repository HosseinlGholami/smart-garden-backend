from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from garden.models import Garden, GardenAccess, Valve, Power, Pump, Schedule, SystemLog, WaterUsage, PowerConsumption

User = get_user_model()

class Command(BaseCommand):
    help = 'Load mock data from frontend into the database'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Loading mock data...'))
        
        # Get the first garden or create a default one if none exists
        try:
            garden = Garden.objects.first()
            if not garden:
                garden = Garden.objects.create(name="Default Garden", description="Default garden for testing")
                self.stdout.write(self.style.SUCCESS(f'Created default garden: {garden.name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Using existing garden: {garden.name}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting garden: {e}'))
            return
        
        # Create guest user if it doesn't exist
        try:
            guest_email = 'guest@smartgarden.com'
            guest_user, created = User.objects.get_or_create(
                email=guest_email,
                defaults={
                    'first_name': 'Guest',
                    'last_name': 'User',
                    'role': 'staff',
                    'is_active': True
                }
            )
            
            if created:
                guest_user.set_password('guest123')  # Set a simple password
                guest_user.save()
                self.stdout.write(self.style.SUCCESS(f'Created guest user: {guest_email}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Using existing guest user: {guest_email}'))
                
            # Give guest user access to the garden
            garden_access, access_created = GardenAccess.objects.get_or_create(
                user=guest_user,
                garden=garden,
                defaults={'role': 'staff'}
            )
            
            if access_created:
                self.stdout.write(self.style.SUCCESS(f'Granted guest user access to garden: {garden.name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Guest user already has access to garden: {garden.name}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating guest user: {e}'))
            
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        Valve.objects.filter(garden=garden).delete()
        Power.objects.filter(garden=garden).delete()
        Pump.objects.filter(garden=garden).delete()
        Schedule.objects.filter(garden=garden).delete()
        SystemLog.objects.filter(garden=garden).delete()
        WaterUsage.objects.filter(garden=garden).delete()
        PowerConsumption.objects.filter(garden=garden).delete()
        
        # Create mock valves
        self.stdout.write('Creating valves...')
        mock_valves = [
            {"garden": garden, "number": 1, "status": "off", "duration": 300},
            {"garden": garden, "number": 2, "status": "off", "duration": 300},
            {"garden": garden, "number": 3, "status": "off", "duration": 300},
        ]
        
        for valve_data in mock_valves:
            Valve.objects.create(**valve_data)
        
        # Create power
        self.stdout.write('Creating power status...')
        Power.objects.create(garden=garden, status="on")
        
        # Create pump
        self.stdout.write('Creating pump status...')
        Pump.objects.create(garden=garden, status="off")
        
        # Create system logs
        self.stdout.write('Creating system logs...')
        mock_logs = [
            {"garden": garden, "event": "Valve 1 turned on", "source": "Automatic", "timestamp": timezone.now() - timedelta(hours=2)},
            {"garden": garden, "event": "Valve 2 turned off", "source": "Manual", "timestamp": timezone.now() - timedelta(hours=1)},
            {"garden": garden, "event": "System started", "source": "System", "timestamp": timezone.now() - timedelta(days=1)},
            {"garden": garden, "event": "Emergency stop activated", "source": "Manual", "timestamp": timezone.now() - timedelta(days=2)},
        ]
        
        for log_data in mock_logs:
            SystemLog.objects.create(**log_data)
        
        # Create schedules
        self.stdout.write('Creating schedules...')
        mock_schedules = [
            {
                "garden": garden,
                "startTime": "08:00 AM",
                "duration": "30 minutes",
                "target": "Valve 1",
                "repeat": "Daily",
                "isActive": True
            },
            {
                "garden": garden,
                "startTime": "01:00 PM",
                "duration": "60 minutes",
                "target": "Valve 2",
                "repeat": "Weekly",
                "days": ["monday"],
                "isActive": False
            }
        ]
        
        for schedule_data in mock_schedules:
            Schedule.objects.create(**schedule_data)
        
        # Create water usage data
        self.stdout.write('Creating water usage data...')
        mock_water_usage = [
            {"garden": garden, "period": "Week 1", "valve1": 10, "valve2": 5, "valve3": 7},
            {"garden": garden, "period": "Week 2", "valve1": 12, "valve2": 6, "valve3": 8},
        ]
        
        for usage_data in mock_water_usage:
            WaterUsage.objects.create(**usage_data)
        
        # Create power consumption data
        self.stdout.write('Creating power consumption data...')
        today = timezone.now().date()
        mock_power_consumption = [
            {"garden": garden, "time": "00:00", "consumption": 10, "date": today},
            {"garden": garden, "time": "01:00", "consumption": 12, "date": today},
            {"garden": garden, "time": "02:00", "consumption": 8, "date": today},
            {"garden": garden, "time": "03:00", "consumption": 5, "date": today},
            {"garden": garden, "time": "04:00", "consumption": 7, "date": today},
            {"garden": garden, "time": "05:00", "consumption": 9, "date": today},
            {"garden": garden, "time": "06:00", "consumption": 11, "date": today},
            {"garden": garden, "time": "07:00", "consumption": 14, "date": today},
            {"garden": garden, "time": "08:00", "consumption": 16, "date": today},
            {"garden": garden, "time": "09:00", "consumption": 18, "date": today},
            {"garden": garden, "time": "10:00", "consumption": 15, "date": today},
            {"garden": garden, "time": "11:00", "consumption": 13, "date": today},
            {"garden": garden, "time": "12:00", "consumption": 11, "date": today},
        ]
        
        for consumption_data in mock_power_consumption:
            PowerConsumption.objects.create(**consumption_data)
            
        self.stdout.write(self.style.SUCCESS('Successfully loaded mock data into the database!')) 