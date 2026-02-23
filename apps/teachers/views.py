from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
# from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .models import TeacherProfile
from .serializers import TeacherProfileSerializer, TeacherProfileCreateSerializer
from utils.permissions import IsPrincipal


class TeacherProfileViewSet(ModelViewSet):
    queryset = TeacherProfile.objects.all()
    serializer_class = TeacherProfileSerializer
    permission_classes = [IsAuthenticated, IsPrincipal]
    filter_backends = [SearchFilter]
    search_fields = ['user__username', 'subject', 'qualification']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TeacherProfileCreateSerializer
        return TeacherProfileSerializer