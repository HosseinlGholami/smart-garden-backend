from django.urls import path
from .views import *

urlpatterns = [
    path('trf-param/', TRFParameterListView.as_view(), name='trf-param'),
    path('trf-device/', SensorPlaceListView.as_view(), name='trf-device'),
    path('trf-cmd/', UserConfigListCreateAPIView.as_view(), name='trf-change'),
]
