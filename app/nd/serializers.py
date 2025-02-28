from rest_framework import serializers
from .models import *
from .util import *

from djoser.serializers import UserSerializer


class TRFParameterSerializer(serializers.ModelSerializer):
    modified_name = serializers.SerializerMethodField()

    class Meta:
        model = TRFParam
        fields = ["param_name", "param_id", "modified_name"]

    def get_modified_name(self, obj):
        request = self.context.get("request")
        device_id = request.query_params.get("device_id") if request else None

        param_name = obj.param_name
        param_id = obj.param_id

        if "PARAMS_INPUT_NUM" in param_name:
            temp_param = param_name.split("_")[0:4]
            related_param = "_".join(temp_param)

            # Filter SensorPlace based on device_id if provided
            sensor_places_filter = SensorPlace.objects.filter(pin_num__param_name=related_param)
            if device_id:
                sensor_places_filter = sensor_places_filter.filter(device_id=device_id)

            if sensor_places_filter.exists():
                for sensor in sensor_places_filter:
                    remain = param_name.split(related_param)[-1]
                    return f"{sensor.section}{remain}" if remain else f"{sensor.section}_VALUE"

        return param_name

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