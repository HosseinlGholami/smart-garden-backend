from rest_framework import serializers
from .models import *
from .util import *

from djoser.serializers import UserSerializer


class CustomUserSerializer(serializers.ModelSerializer):
    user_role = serializers.PrimaryKeyRelatedField(
        queryset=UserRole.objects.all()
    )  # Allows setting user_role by ID instead of a nested object

    class Meta:
        model = CustomUser
        fields = ["username", "first_name", "last_name", "user_role", "email"]



class TRFParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TRFParam
        fields = ["param_name", "param_id"]

class SensorPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorPlace
        fields = ['device_id','pin_num','section']

class TRFUserConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = TRFUserConfig
        fields = ['device_id', 'command_type', 'parameter_id', 'value']

class DeviceOtaSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=255)

    def validate_device_id(self, value):
        if not SensorPlace.objects.filter(device_id=value).exists():
            raise serializers.ValidationError("Device ID does not exist.")
        return value