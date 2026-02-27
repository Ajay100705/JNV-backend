from rest_framework.routers import DefaultRouter
from .views import HouseMasterViewSet, HouseViewSet

router = DefaultRouter()
router.register("house-masters", HouseMasterViewSet, basename="house-master")
router.register("houses", HouseViewSet, basename="house")

urlpatterns = router.urls