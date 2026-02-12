from uuid import uuid4
from django.db import models
from django.contrib.auth.models import AbstractUser

from utils.choices import ROLE



class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE, default='parent')


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class ParentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="parent_profile"
    )
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.user.email


class TeacherProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="teacher_profile"
    )
    employee_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.user.email
