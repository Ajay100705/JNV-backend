from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.choices import ROLE, GENDER


class User(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE)
    gender = models.CharField(max_length=10, choices=GENDER)


    def __str__(self):
        return self.username
    

