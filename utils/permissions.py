from rest_framework.permissions import BasePermission



class IsPrincipal(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.roll == 'principal'
        )

class IsTeacherOrPrincipal(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.roll in ['teacher', 'principal']
        )

class IsParent(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.roll == 'parent'
        )
