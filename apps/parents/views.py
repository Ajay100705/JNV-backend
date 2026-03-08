from rest_framework import viewsets
from rest_framework.views import APIView, Response
from .models import Parent
from .serializers import ParentSerializer, ParentUpdateSerializer
from apps.students.models import Student
from rest_framework.permissions import IsAuthenticated
from utils.permissions import IsPrincipal
from rest_framework import status

class ParentViewset(viewsets.ModelViewSet):
    queryset = Parent.objects.prefetch_related(
        "children__user",
        "children__classroom",
        "children__house",
    )
    serializer_class = ParentSerializer
    permission_classes = [IsAuthenticated, IsPrincipal]
    
class ParentProfileview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        parent = request.user.parent_profile
        serializer = ParentSerializer(parent)
        return Response(serializer.data)
    
    def patch(self, request):
        parent = request.user.parent_profile
        serializer = ParentUpdateSerializer(parent, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
    