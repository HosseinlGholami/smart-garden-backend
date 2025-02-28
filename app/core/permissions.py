from rest_framework.permissions import BasePermission
from core.enums import AccessLevels

class HasMaintainerPermission(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.access_level >= AccessLevels.MAINTAINER.value
        )


class HasDeveloperPermission(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.access_level >= AccessLevels.DEVELOPER.value
        )


class HasOperatorPermission(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.access_level >= AccessLevels.OPERATOR.value
        )


class HasViewerPermission(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.access_level >= AccessLevels.VIEWER.value
        )
