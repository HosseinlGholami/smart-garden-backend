from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Permission to only allow admin users to access the view.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == 'admin'


class IsManager(permissions.BasePermission):
    """
    Permission to only allow manager users or higher to access the view.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['admin', 'manager']


class IsStaff(permissions.BasePermission):
    """
    Permission to only allow staff users or higher to access the view.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['admin', 'manager', 'staff'] 