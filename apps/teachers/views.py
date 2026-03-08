from rest_framework.views import APIView, Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.filters import SearchFilter

from .models import TeacherProfile
from .serializers import TeacherProfileSerializer, TeacherProfileCreateSerializer
from utils.permissions import IsPrincipal, IsTeacherOrPrincipal


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
    
class UpdateTeacherProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        if request.user.role not in ['principal', 'teacher']:
            return Response({"detail": "Only principals or teachers can update their profile."}, status=status.HTTP_403_FORBIDDEN)
        
        profile = request.user.teacher_profile

        serializer = TeacherProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        print(serializer.errors)
        return Response(serializer.errors, status=400)

