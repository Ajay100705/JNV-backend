from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/', include('apps.accounts.urls')),
    path('classes/', include('apps.classes.urls')),
    path('students/', include('apps.students.urls')),
    path('teachers/', include('apps.teachers.urls')),
    path('core/', include('apps.core.urls')),
    path('houses/', include('apps.houses.urls')),
    path('parents/', include('apps.parents.urls')),
    path('academic/', include('apps.academic.urls')),
    path('attendance/', include('apps.attendance.urls')),
]
