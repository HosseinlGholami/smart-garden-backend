from django.db import models
from django.conf import settings


class Garden(models.Model):
    """Model for representing a garden in the system."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class GardenAccess(models.Model):
    """Model for handling user access to gardens with specific roles."""
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='garden_accesses')
    garden = models.ForeignKey(Garden, on_delete=models.CASCADE, related_name='user_accesses')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    
    class Meta:
        unique_together = ('user', 'garden')
        verbose_name_plural = 'Garden Accesses'
    
    def __str__(self):
        return f"{self.user} - {self.garden} ({self.role})"


# New models for Smart Garden System
class Valve(models.Model):
    """Model for garden valves."""
    garden = models.ForeignKey(Garden, on_delete=models.CASCADE, related_name='valves')
    number = models.IntegerField()
    status = models.CharField(max_length=10, choices=[('on', 'On'), ('off', 'Off')], default='off')
    duration = models.IntegerField(default=300)  # Duration in seconds
    last_active = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('garden', 'number')
    
    def __str__(self):
        return f"{self.garden.name} - Valve {self.number} - {self.status}"


class Power(models.Model):
    """Model for power management."""
    garden = models.ForeignKey(Garden, on_delete=models.CASCADE, related_name='power_records')
    status = models.CharField(max_length=10, choices=[('on', 'On'), ('off', 'Off')], default='off')
    last_status_change = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Power"
    
    def __str__(self):
        return f"{self.garden.name} - Power - {self.status}"


class Pump(models.Model):
    """Model for water pump."""
    garden = models.ForeignKey(Garden, on_delete=models.CASCADE, related_name='pumps')
    status = models.CharField(max_length=10, choices=[('on', 'On'), ('off', 'Off')], default='off')
    last_status_change = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.garden.name} - Pump - {self.status}"


class SystemLog(models.Model):
    """Model for system logs."""
    garden = models.ForeignKey(Garden, on_delete=models.CASCADE, related_name='system_logs')
    event = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=20, choices=[
        ('Manual', 'Manual'),
        ('Automatic', 'Automatic'),
        ('System', 'System')
    ])
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.garden.name} - {self.event} - {self.timestamp}"


class Schedule(models.Model):
    """Model for watering schedules."""
    REPEAT_CHOICES = [
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Once', 'Once')
    ]
    
    garden = models.ForeignKey(Garden, on_delete=models.CASCADE, related_name='schedules')
    startTime = models.CharField(max_length=10)  # Format: "08:00 AM"
    duration = models.CharField(max_length=20)   # Format: "30 minutes"
    target = models.CharField(max_length=20)     # Format: "Valve 1"
    repeat = models.CharField(max_length=10, choices=REPEAT_CHOICES)
    days = models.JSONField(null=True, blank=True)  # For weekly schedules: ["monday", "wednesday"]
    isActive = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.garden.name} - {self.target} at {self.startTime} - {self.repeat}"


class WaterUsage(models.Model):
    """Model for water usage data."""
    garden = models.ForeignKey(Garden, on_delete=models.CASCADE, related_name='water_usages')
    period = models.CharField(max_length=20)  # Week 1, Week 2, etc.
    valve1 = models.FloatField(default=0)
    valve2 = models.FloatField(default=0)
    valve3 = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.garden.name} - Water usage for {self.period}"


class PowerConsumption(models.Model):
    """Model for power consumption data."""
    garden = models.ForeignKey(Garden, on_delete=models.CASCADE, related_name='power_consumptions')
    time = models.CharField(max_length=10)  # Format: "00:00"
    consumption = models.FloatField()
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.garden.name} - Power consumption at {self.time}: {self.consumption}" 