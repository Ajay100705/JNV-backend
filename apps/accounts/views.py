from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from utils.permissions import(
    IsParent,
    IsTeacherOrPrincipal,
    IsPrincipal
)
from .serializers import( 
    UserSerializer,
    ParentCreateSerializer,
    LoginSerializer,
    TeacherCreateSerializer,
      
      )


class LoginView(APIView):
    permission_classes = []
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Login successful",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "roll": user.roll,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
            }, status=200)

        return Response({
            'message': 'User creation failed',
            'errors': serializer.errors
        }, status=400)
        

class ParentViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(roll='parent')
    serializer_class = ParentCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create']:
            return [IsAuthenticated(), IsTeacherOrPrincipal()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsPrincipal()]
        
        return super().get_permissions()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ParentCreateSerializer
        return UserSerializer
        

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(roll='teacher')
    serializer_class = TeacherCreateSerializer
    permission_classes = [IsAuthenticated, IsPrincipal]

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']:
            return [IsPrincipal()]
        
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return TeacherCreateSerializer
        return UserSerializer
        

