from rest_framework import permissions
from .models import GardenAccess


class HasGardenAccess(permissions.BasePermission):
    """
    Base permission to check if the user has access to a garden.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Superusers can access everything
        if request.user.is_superuser:
            return True
            
        # For list views, allow access, filtering will happen in the queryset
        if view.action == 'list':
            return True
            
        # For other actions, check if garden_id is provided in kwargs or query params
        garden_id = view.kwargs.get('garden_id') or request.query_params.get('garden_id')
        
        if garden_id is None:
            # If no garden is specified, deny access
            return False
            
        # Check if the user has access to this garden
        return GardenAccess.objects.filter(
            user=request.user,
            garden_id=garden_id
        ).exists()
    
    def has_object_permission(self, request, view, obj):
        # Check if obj has a garden attribute
        if hasattr(obj, 'garden'):
            garden = obj.garden
        elif hasattr(obj, 'garden_id'):
            garden_id = obj.garden_id
            return GardenAccess.objects.filter(
                user=request.user,
                garden_id=garden_id
            ).exists()
        else:
            # If the object doesn't have a garden relation, deny access
            return False
            
        # Check user's access to this garden
        return GardenAccess.objects.filter(
            user=request.user,
            garden=garden
        ).exists()


class IsGardenAdmin(HasGardenAccess):
    """
    Permission to only allow garden admins to access the view or object.
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
            
        # For list views, allow access, filtering will happen in queryset
        if view.action == 'list':
            return True
            
        garden_id = view.kwargs.get('garden_id') or request.query_params.get('garden_id')
        
        if garden_id is None:
            return False
            
        return GardenAccess.objects.filter(
            user=request.user,
            garden_id=garden_id,
            role='admin'
        ).exists()
    
    def has_object_permission(self, request, view, obj):
        if not super().has_object_permission(request, view, obj):
            return False
            
        if hasattr(obj, 'garden'):
            garden = obj.garden
        elif hasattr(obj, 'garden_id'):
            garden_id = obj.garden_id
            return GardenAccess.objects.filter(
                user=request.user,
                garden_id=garden_id,
                role='admin'
            ).exists()
        else:
            return False
            
        return GardenAccess.objects.filter(
            user=request.user,
            garden=garden,
            role='admin'
        ).exists()


class IsGardenManager(HasGardenAccess):
    """
    Permission to only allow garden managers or admins to access the view or object.
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
            
        # For list views, allow access, filtering will happen in queryset
        if view.action == 'list':
            return True
            
        garden_id = view.kwargs.get('garden_id') or request.query_params.get('garden_id')
        
        if garden_id is None:
            return False
            
        return GardenAccess.objects.filter(
            user=request.user,
            garden_id=garden_id,
            role__in=['admin', 'manager']
        ).exists()
    
    def has_object_permission(self, request, view, obj):
        if not super().has_object_permission(request, view, obj):
            return False
            
        if hasattr(obj, 'garden'):
            garden = obj.garden
        elif hasattr(obj, 'garden_id'):
            garden_id = obj.garden_id
            return GardenAccess.objects.filter(
                user=request.user,
                garden_id=garden_id,
                role__in=['admin', 'manager']
            ).exists()
        else:
            return False
            
        return GardenAccess.objects.filter(
            user=request.user,
            garden=garden,
            role__in=['admin', 'manager']
        ).exists()


class IsGardenStaff(HasGardenAccess):
    """
    Permission to allow any role (admin, manager, staff) to access the view or object.
    """
    # This class just inherits from HasGardenAccess without additional restrictions
    pass 