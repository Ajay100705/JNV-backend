from apps.accounts.models import ParentProfile, TeacherProfile
from django.db import models
from utils.choices import GENDER



class Class(models.Model):
    name = models.CharField(max_length=20)   
    section = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.name}{self.section}"


class House(models.Model):
    name = models.CharField(max_length=20, unique=True)
    house_master = models.ForeignKey(
        TeacherProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


class Student(models.Model):
    admission_number = models.CharField(max_length=20, unique=True)
    roll_number = models.PositiveIntegerField()

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER)
    
    parent = models.ForeignKey(ParentProfile, related_name='students', on_delete=models.CASCADE)
    
    student_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True)
    
    house = models.ForeignKey(House, on_delete=models.SET_NULL, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    admission_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    



