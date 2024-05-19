from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsAdminOrRegistrationOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in 'POST':
            return True
        return bool(request.user.is_staff)


class IsAdminOrAuthenticatedUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return bool(request.user and request.user.is_staff)


class AuthenticatedUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False


class AllowOnlyAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
         return bool(request.user.is_staff)