from rest_framework.routers import DefaultRouter
from apps.students.views import StudentViewSet

router = DefaultRouter()
router.register('', StudentViewSet)

urlpatterns = router.urls