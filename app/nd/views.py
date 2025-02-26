from django.db.models import Case, When, IntegerField

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated , AllowAny

from .models import *
from .serializers import *
import time

from .tasks import process_user_config
import logging
logger = logging.getLogger(__name__)


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

    def list(self, request, *args, **kwargs):
        user_role = request.user.user_role

        if user_role.advance_control == False:
            queryset =  TRFParam.objects.filter(is_advance=False)
        else:
            queryset =  TRFParam.objects.all()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SensorPlaceListView(generics.ListAPIView):
    queryset = SensorPlace.objects.all()
    serializer_class = SensorPlaceSerializer

class UserConfigListCreateAPIView(generics.CreateAPIView):
    serializer_class = TRFUserConfigSerializer

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