from django.urls import path, include
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

class CustomUserViewSet(DjoserUserViewSet):
    permission_classes = [IsAuthenticated]
    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
urlpatterns = [
    # Only include the Djoser endpoints you want to expose
    path('', include('djoser.urls.jwt')),
    path('users/me/', CustomUserViewSet.as_view({'get': 'retrieve'}), name='user-me'),
]
