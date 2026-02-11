from rest_framework.permissions import BasePermission



class IsPrincipal(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'principal'
        )

class IsTeacherOrPrincipal(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ['teacher', 'principal']
        )

class IsParent(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'parent'
        )
