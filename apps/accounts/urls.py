from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView, ParentViewSet, TeacherViewSet, MeView


router = DefaultRouter()
router.register(r'parents', ParentViewSet, basename='parent')
router.register(r'teachers', TeacherViewSet, basename='teacher')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('me/', MeView.as_view()),

]
