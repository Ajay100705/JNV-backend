from rest_framework.permissions import BasePermission
from apps.academic.models import ClassTeacher
from apps.academic.utils import get_current_academic_year



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
    
class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'


class IsParent(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'parent'
        )
class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'


class CanMarkAttendance(BasePermission):

    def has_permission(self, request, view):
        print("CHECKING has_permission")
        # Check teacher role
        if not request.user.is_authenticated:
            print("User not authenticated")
            return False

        if request.user.role != "teacher":
            print("User role not teacher:", request.user.role)
            return False

        if not hasattr(request.user, "teacher_profile"):
            print("No teacher_profile")
            return False
        
        print("Permission passed")
        return True


    def has_object_permission(self, request, view, obj):

        teacher = request.user.teacher_profile

        print("Logged teacher:", teacher)
        print("Timetable teacher:", obj.teacher)

        # Subject teacher
        if obj.teacher == teacher:
            print("Subject teacher allowed")
            return True

        # Class teacher override
        class_teacher = ClassTeacher.objects.filter(
            teacher=teacher,
            classroom=obj.classroom,
            academic_year=get_current_academic_year()
        ).exists()
    
        print("Class teacher override:", class_teacher)
        return class_teacher
