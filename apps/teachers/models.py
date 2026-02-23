from django.db import models
from django.conf import settings

class TeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, null=True, blank=True)
    qualification = models.CharField(max_length=255)
    experience_years = models.PositiveIntegerField()
    date_of_joining = models.DateField()
    photo = models.ImageField(upload_to='teacher_photos/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - Teacher - {self.subject}"
