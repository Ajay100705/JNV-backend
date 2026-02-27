from rest_framework import viewsets
from .models import Parent
from .serializers import ParentSerializer
from apps.students.models import Student
from rest_framework.permissions import IsAuthenticated
from utils.permissions import IsPrincipal

class ParentViewset(viewsets.ModelViewSet):
    queryset = Parent.objects.prefetch_related(
        "children__user",
        "children__classroom",
        "children__house",
    )
    serializer_class = ParentSerializer
    permission_classes = [IsAuthenticated, IsPrincipal]

    