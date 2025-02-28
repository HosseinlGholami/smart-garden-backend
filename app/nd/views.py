from django.db.models import Case, When, IntegerField

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated , AllowAny

from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import *
from .serializers import *
import time
from collections import defaultdict

from .tasks import process_user_config
import logging
logger = logging.getLogger(__name__)

from core.permissions import *
from core.enums import AccessLevels

# file server for OTA ESP32
from django.http import FileResponse, Http404
from django.conf import settings
import os

class FileDownloadView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, filename):
        # Sanitize filename
        filename = os.path.basename(filename)

        file_path = os.path.join(settings.OTA_DIR, filename)

        if os.path.exists(file_path) and file_path.startswith(os.path.abspath(settings.OTA_DIR)):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
        else:
            raise Http404("File does not exist")



class TRFParameterListView(generics.ListAPIView):
    serializer_class = TRFParameterSerializer
    permission_classes = [HasViewerPermission]

    @extend_schema(
        # Define the `device_id` query parameter
        parameters=[
            OpenApiParameter(
                name="device_id",
                type=str,
                location=OpenApiParameter.QUERY,
                description="ID of the device to filter parameters",
                required=True,
            ),
        ],
        # Define the response schema
        responses={200: TRFParameterSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        # Get device_id from query parameters
        device_id = self.request.query_params.get('device_id')

        # handle the acess level
        access_level = self.request.user.access_level
        
        if access_level < AccessLevels.OPERATOR.value:
            queryset = TRFParam.objects.filter(is_advance=False)
        else:
            queryset = TRFParam.objects.all()


        # Validate that device_id is provided
        if not device_id:
            raise ValidationError({"error": "device_id is required as a query parameter"})

        # Validate that the device_id exists in the SensorPlace table
        if not SensorPlace.objects.filter(device_id=device_id).exists():
            raise ValidationError({"error": "Invalid device_id"})

        return queryset


    def list(self, request, *args, **kwargs):
        # Get the queryset
        queryset = self.get_queryset()

        # Get device_id from query parameters
        device_id = request.query_params.get('device_id')

        # Initialize response data
        response_data = []

        # Process each parameter in the queryset
        for param in queryset:
            param_name = param.param_name
            param_id = param.param_id
            # Check if the parameter name contains "PARAMS_INPUT_NUM"
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
                        if remain:
                            modified_name = f"{sensor.section}{remain}"
                        else:
                            modified_name = f"{sensor.section}_SENSOR_VALUE"
                        logger.debug(f"modified_name: {modified_name}")
                        response_data.append({
                            "param_name": modified_name,
                            "param_id": param_id
                        })
            else:
                response_data.append({
                    "param_name": param_name,
                    "param_id": param_id
                })

        return Response(response_data)


class SensorPlaceListView(generics.ListAPIView):
    permission_classes = [HasViewerPermission]
    queryset = SensorPlace.objects.all()
    serializer_class = SensorPlaceSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        grouped_data = defaultdict(lambda: {"section": []})

        for sensor in queryset:
            grouped_data[sensor.device_id]["section"].append(sensor.section)

        return Response(grouped_data)
        

class UserConfigListCreateAPIView(generics.CreateAPIView):
    serializer_class = TRFUserConfigSerializer
    permission_classes = [HasOperatorPermission]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            
            hub_id = serializer.data.get("device_id")
            pckt_type = serializer.data.get("command_type")
            address = serializer.data.get("parameter_id")
            value = serializer.data.get("value")
            logger.debug(f"{hub_id, pckt_type, address, value}")
            # Get the result from Celery task
            try:
                # Wait for the task result with a timeout
                result = process_user_config.delay(int(hub_id), int(pckt_type), int(address), int(value)).get(timeout=5)
            except TimeoutError:
                # Handle timeout error
                result = "Task execution timed out"
            except Exception as e:
                # Handle other exceptions
                result = f"Error: {e}"
            return Response({'result': result, 'data': serializer.data}, status=201)
        return Response(serializer.errors, status=400)