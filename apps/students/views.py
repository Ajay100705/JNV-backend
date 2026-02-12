from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Student
from .serializers import StudentSerializer
from rest_framework.exceptions import PermissionDenied


class StudentViewSet(ModelViewSet):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'principal':
            return Student.objects.all()
        
        if user.role == 'teacher':
            return Student.objects.all()
        
        if user.role == 'parent':
            return Student.objects.filter(parent__user=user)
        
        return Student.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.role != "principal":
            raise PermissionDenied("Only principals can add students.")
        serializer.save()
