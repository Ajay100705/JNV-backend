from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.choices import ROLE, GENDER


class User(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE, default='principal')
    gender = models.CharField(max_length=10, choices=GENDER, default='male')


    def __str__(self):
        return self.username
    
class PrincipalProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='principal_profile')
    phone1 = models.CharField(max_length=20, blank=True, null=True)
    phone2 = models.CharField(max_length=20, blank=True, null=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    present_address = models.TextField(blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Principal Profile"
    
    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

