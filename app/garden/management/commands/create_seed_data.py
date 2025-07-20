from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from app.garden.models import (
    Garden, GardenAccess, Valve, Power, Pump, Schedule, SystemLog,
    WaterUsage, PowerConsumption
)
import random
from datetime import datetime, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Create seed data for the smart garden system'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating seed data...'))
        
        # Create admin user if doesn't exist
        admin_email = 'admin@admin.com'
        admin_user, created = User.objects.get_or_create(
            email=admin_email,
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_email}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Using existing admin user: {admin_email}'))
        
        # Create Haj-Ebi garden
        haj_ebi_garden, created = Garden.objects.get_or_create(
            name="Haj-Ebi",
            defaults={
                'description': "Main irrigation garden with automated watering system",
                'location': "Haj-Ebi Farm, Northern Section"
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created garden: {haj_ebi_garden.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Using existing garden: {haj_ebi_garden.name}'))
        
        # Give admin user Manager access to Haj-Ebi garden
        garden_access, access_created = GardenAccess.objects.get_or_create(
            user=admin_user,
            garden=haj_ebi_garden,
            defaults={'role': 'manager'}
        )
        
        if access_created:
            self.stdout.write(self.style.SUCCESS(f'Granted {garden_access.role} access to {admin_user.email} for {haj_ebi_garden.name}'))
        else:
            # Update role if it exists
            garden_access.role = 'manager'
            garden_access.save()
            self.stdout.write(self.style.SUCCESS(f'Updated access role to {garden_access.role} for {admin_user.email}'))
        
        # Create staff user for testing role restrictions
        staff_email = 'staff@admin.com'
        staff_user, staff_created = User.objects.get_or_create(
            email=staff_email,
            defaults={
                'first_name': 'Staff',
                'last_name': 'User',
                'role': 'staff',
                'is_active': True
            }
        )
        
        if staff_created:
            staff_user.set_password('staff123')
            staff_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created staff user: {staff_email}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Using existing staff user: {staff_email}'))
        
        # Give staff user Staff access to Haj-Ebi garden
        staff_garden_access, staff_access_created = GardenAccess.objects.get_or_create(
            user=staff_user,
            garden=haj_ebi_garden,
            defaults={'role': 'staff'}
        )
        
        if staff_access_created:
            self.stdout.write(self.style.SUCCESS(f'Granted {staff_garden_access.role} access to {staff_user.email} for {haj_ebi_garden.name}'))
        else:
            staff_garden_access.role = 'staff'
            staff_garden_access.save()
            self.stdout.write(self.style.SUCCESS(f'Updated access role to {staff_garden_access.role} for {staff_user.email}'))
        
        # Create valves for the garden
        valve_configs = [
            {'number': 1, 'status': 'off', 'duration': 300},
            {'number': 2, 'status': 'off', 'duration': 450},
            {'number': 3, 'status': 'off', 'duration': 600},
            {'number': 4, 'status': 'off', 'duration': 900},
        ]
        
        for config in valve_configs:
            valve, created = Valve.objects.get_or_create(
                garden=haj_ebi_garden,
                number=config['number'],
                defaults={
                    'status': config['status'],
                    'duration': config['duration']
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created valve {valve.number} for {haj_ebi_garden.name}'))
        
        # Create power record for the garden
        power, created = Power.objects.get_or_create(
            garden=haj_ebi_garden,
            defaults={'status': 'on'}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created power record for {haj_ebi_garden.name}'))
        
        # Create pump record for the garden
        pump, created = Pump.objects.get_or_create(
            garden=haj_ebi_garden,
            defaults={'status': 'off'}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created pump record for {haj_ebi_garden.name}'))
        
        # Create some schedules
        schedules = [
            {
                'startTime': '07:00',
                'duration': '30 minutes',
                'target': 'Valve 1',
                'repeat': 'Daily',
                'isActive': True
            },
            {
                'startTime': '18:00',
                'duration': '20 minutes',
                'target': 'Valve 2',
                'repeat': 'Daily',
                'isActive': True
            },
            {
                'startTime': '08:00',
                'duration': '45 minutes',
                'target': 'Valve 3',
                'repeat': 'Weekly',
                'isActive': False
            }
        ]
        
        for schedule_data in schedules:
            schedule, created = Schedule.objects.get_or_create(
                garden=haj_ebi_garden,
                startTime=schedule_data['startTime'],
                target=schedule_data['target'],
                defaults={
                    'duration': schedule_data['duration'],
                    'repeat': schedule_data['repeat'],
                    'isActive': schedule_data['isActive']
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created schedule: {schedule.target} at {schedule.startTime}'))
        
        # Create system logs
        log_events = [
            {'event': 'System startup completed', 'source': 'System'},
            {'event': 'Valve 1 opened for scheduled watering', 'source': 'Automatic'},
            {'event': 'Valve 1 closed after scheduled duration', 'source': 'Automatic'},
            {'event': 'Morning watering cycle completed', 'source': 'Automatic'},
            {'event': 'Pump maintenance check passed', 'source': 'System'},
            {'event': 'User manually opened Valve 2', 'source': 'Manual'},
            {'event': 'Evening watering schedule started', 'source': 'Automatic'},
            {'event': 'All systems operating normally', 'source': 'System'},
        ]
        
        # Clear old logs for this garden
        SystemLog.objects.filter(garden=haj_ebi_garden).delete()
        
        for i, log_data in enumerate(log_events):
            timestamp = timezone.now() - timedelta(hours=i*2)  # Spread logs over the last 16 hours
            SystemLog.objects.create(
                garden=haj_ebi_garden,
                event=log_data['event'],
                source=log_data['source'],
                timestamp=timestamp
            )
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(log_events)} system logs'))
        
        # Create water usage data
        WaterUsage.objects.filter(garden=haj_ebi_garden).delete()
        
        for i in range(7):  # Last 7 days
            date = timezone.now() - timedelta(days=i)
            WaterUsage.objects.create(
                garden=haj_ebi_garden,
                period=f'Day {i+1}',
                valve1=random.uniform(15, 25),
                valve2=random.uniform(10, 20),
                valve3=random.uniform(8, 15),
                timestamp=date
            )
        
        self.stdout.write(self.style.SUCCESS('Created water usage data for last 7 days'))
        
        # Create power consumption data
        PowerConsumption.objects.filter(garden=haj_ebi_garden).delete()
        
        today = timezone.now().date()
        for hour in range(24):
            time_str = f'{hour:02d}:00'
            consumption = random.uniform(20, 60) if 6 <= hour <= 20 else random.uniform(10, 25)
            
            PowerConsumption.objects.create(
                garden=haj_ebi_garden,
                time=time_str,
                consumption=consumption,
                date=today
            )
        
        self.stdout.write(self.style.SUCCESS('Created power consumption data for today'))
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n✅ Seed data creation completed!\n'
                f'🏡 Garden: {haj_ebi_garden.name}\n'
                f'👤 Admin User: {admin_email} (password: admin) - Manager role\n'
                f'👤 Staff User: {staff_email} (password: staff123) - Staff role\n'
                f'🚰 Valves: {len(valve_configs)} valves created\n'
                f'📅 Schedules: {len(schedules)} schedules created\n'
                f'📊 Sample data: Logs, water usage, and power consumption added\n'
                f'\n💡 Test role restrictions:\n'
                f'   • Admin/Manager users can select different gardens\n'
                f'   • Staff users are automatically assigned to their first garden\n'
            )
        ) 