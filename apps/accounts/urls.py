from django.urls import path
from .views import LoginView, MeView, UpdatePrincipalProfileView, ChangePasswordView


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('me/', MeView.as_view(), name='me'),
    path('principal/update-profile/', UpdatePrincipalProfileView.as_view(), name='update-principal-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]
