from uuid import uuid4
from django.db import models
from django.contrib.auth.models import AbstractUser

from utils.choices import ROLL



class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(unique=True)
    roll = models.CharField(max_length=20, choices=ROLL, default='parent')


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

