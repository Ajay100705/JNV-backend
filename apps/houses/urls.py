from rest_framework.routers import DefaultRouter, path
from .views import (
    HouseMasterViewSet,
    HouseViewSet, 
    HouseMasterDashboardView, 
    HouseStudentsView, 
    TakeHouseAttendanceView,
    TodayLeaveStudentsView,
    
) 

router = DefaultRouter()
router.register("house-masters", HouseMasterViewSet, basename="house-master")
router.register("houses", HouseViewSet, basename="house")

urlpatterns = router.urls

urlpatterns += [
    path("house-dashboard/", HouseMasterDashboardView.as_view(), name="house-master-dashboard"),
    path("house-students/", HouseStudentsView.as_view(), name="house-students"),
    path("take-house-attendance/", TakeHouseAttendanceView.as_view(), name="take-house-attendance"),
    path("today-leave-students/", TodayLeaveStudentsView.as_view(), name="today-leave-students"),
]