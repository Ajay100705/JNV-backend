from django.db import models
from utils.choices import ROLE
from django.conf import settings


class Parent(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="parent_profile")
    
    role = models.CharField(max_length=20, choices=ROLE, default='parent')
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    job = models.CharField(max_length=100, blank=True, null=True)

    phone1 = models.CharField(max_length=15)
    phone2 = models.CharField(max_length=15, blank=True, null=True)

    email = models.EmailField()

    photo = models.ImageField(upload_to='parent_photos/', blank=True, null=True)

    present_address = models.TextField()
    permanent_address = models.TextField()

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
