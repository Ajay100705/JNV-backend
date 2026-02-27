from rest_framework.routers import DefaultRouter
from .views import DashboardStatsViewSet, HouseWiseStudentCountAPIView
from django.urls import path

router = DefaultRouter()
router.register(r'dashboard-stats', DashboardStatsViewSet, basename='dashboard-stats')

urlpatterns = [
    path("house-wise-students/", HouseWiseStudentCountAPIView.as_view()),
    
]

urlpatterns += router.urls