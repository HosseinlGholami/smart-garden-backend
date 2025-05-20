from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import CustomUserSerializer
from .permissions import IsAdmin, IsManager


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated, IsManager]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return User.objects.all()
        elif user.role == 'manager':
            # Managers can see staff and other managers but not admins
            return User.objects.filter(role__in=['manager', 'staff'])
        return User.objects.filter(id=user.id)  # Staff users can only see themselves
    
    @action(detail=False, permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get the current authenticated user information."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def activate(self, request, pk=None):
        """Activate or deactivate a user."""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        return Response({'status': 'user activated' if user.is_active else 'user deactivated'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def change_role(self, request, pk=None):
        """Change user role."""
        user = self.get_object()
        role = request.data.get('role')
        
        if role not in [r[0] for r in User.ROLE_CHOICES]:
            return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.role = role
        user.save()
        return Response({'status': f'user role changed to {role}'})
