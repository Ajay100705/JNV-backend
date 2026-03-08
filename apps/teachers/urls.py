from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import TeacherProfileViewSet, UpdateTeacherProfileView

router = DefaultRouter()
router.register("", TeacherProfileViewSet, basename="teachers")

urlpatterns = [
    path("update-profile/", UpdateTeacherProfileView.as_view(), name="update-teacher-profile"),
]

urlpatterns += router.urls