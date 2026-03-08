from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import ParentViewset, ParentProfileview

router = DefaultRouter()
router.register("parents", ParentViewset, basename="parent")


urlpatterns = router.urls
urlpatterns += [
    path("profile/", ParentProfileview.as_view(), name="parent-profile"),
]