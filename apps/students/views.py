from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Student
from .serializers import StudentSerializer, StudentCreateSerializer


class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return StudentCreateSerializer
        return StudentSerializer