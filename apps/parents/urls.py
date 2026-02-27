from rest_framework.routers import DefaultRouter
from .views import ParentViewset

router = DefaultRouter()
router.register("parents", ParentViewset, basename="parent")


urlpatterns = router.urls