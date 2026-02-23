from rest_framework.routers import DefaultRouter
from .views import TeacherProfileViewSet

router = DefaultRouter()
router.register("", TeacherProfileViewSet, basename="teachers")

urlpatterns = router.urls
