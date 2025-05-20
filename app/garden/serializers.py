from rest_framework import serializers
from .models import (
    Garden, GardenAccess, Valve, Power, Pump, Schedule, SystemLog,
    WaterUsage, PowerConsumption
)


class GardenSerializer(serializers.ModelSerializer):
    """Serializer for Garden model."""
    class Meta:
        model = Garden
        fields = '__all__'


class GardenAccessSerializer(serializers.ModelSerializer):
    """Serializer for GardenAccess model."""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    garden_name = serializers.CharField(source='garden.name', read_only=True)
    
    class Meta:
        model = GardenAccess
        fields = ('id', 'user', 'garden', 'role', 'user_email', 'garden_name')


# Smart Garden System Serializers
class ValveSerializer(serializers.ModelSerializer):
    """Serializer for Valve model."""
    garden_name = serializers.CharField(source='garden.name', read_only=True)
    
    class Meta:
        model = Valve
        fields = '__all__'


class PowerSerializer(serializers.ModelSerializer):
    """Serializer for Power model."""
    garden_name = serializers.CharField(source='garden.name', read_only=True)
    
    class Meta:
        model = Power
        fields = '__all__'


class PumpSerializer(serializers.ModelSerializer):
    """Serializer for Pump model."""
    garden_name = serializers.CharField(source='garden.name', read_only=True)
    
    class Meta:
        model = Pump
        fields = '__all__'


class SystemLogSerializer(serializers.ModelSerializer):
    """Serializer for SystemLog model."""
    garden_name = serializers.CharField(source='garden.name', read_only=True)
    
    class Meta:
        model = SystemLog
        fields = '__all__'


class ScheduleSerializer(serializers.ModelSerializer):
    """Serializer for Schedule model."""
    garden_name = serializers.CharField(source='garden.name', read_only=True)
    
    class Meta:
        model = Schedule
        fields = '__all__'


class WaterUsageSerializer(serializers.ModelSerializer):
    """Serializer for WaterUsage model."""
    garden_name = serializers.CharField(source='garden.name', read_only=True)
    
    class Meta:
        model = WaterUsage
        fields = '__all__'


class PowerConsumptionSerializer(serializers.ModelSerializer):
    """Serializer for PowerConsumption model."""
    garden_name = serializers.CharField(source='garden.name', read_only=True)
    
    class Meta:
        model = PowerConsumption
        fields = '__all__'


class SystemStatusSerializer(serializers.Serializer):
    """Serializer for system status."""
    garden_id = serializers.IntegerField(write_only=True)
    garden_name = serializers.CharField(read_only=True)
    isConnected = serializers.BooleanField(default=True)
    nextSchedule = serializers.SerializerMethodField()
    lastChecked = serializers.DateTimeField()
    
    def get_nextSchedule(self, obj):
        # Logic to get the next scheduled event
        return {
            'time': obj.get('time', ''),
            'target': obj.get('target', '')
        } 