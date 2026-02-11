from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, email=None, password=None, **kwargs):
        print("EMAIL BACKEND CALLED:", email)

        login = email or username

        if login is None or password is None:
            return None
        
        try:
            user = User.objects.get(email=login)
        except User.DoesNotExist:
            return None
        
        if user.check_password(password):
            return user
        return None