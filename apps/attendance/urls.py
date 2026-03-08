from django.urls import path
from .views import MarkHouseAttendanceView, TodayHouseAttendanceView

urlpatterns = [
    path("house/mark/", MarkHouseAttendanceView.as_view(), name="mark-house-attendance"),
    path("house/today/", TodayHouseAttendanceView.as_view(), name="today-house-attendance"),
]