from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import HouseMaster, House
from .serializers import HouseMasterSerializer, HouseSerializer
from utils.permissions import IsPrincipal


class HouseViewSet(ModelViewSet):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    permission_classes = [IsAuthenticated, IsPrincipal]

class HouseMasterViewSet(ModelViewSet):
    queryset = HouseMaster.objects.all()
    serializer_class = HouseMasterSerializer
    permission_classes = [IsAuthenticated, IsPrincipal]