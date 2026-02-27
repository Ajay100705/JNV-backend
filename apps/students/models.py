from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.classes.models import ClassRoom
from apps.houses.models import House
from apps.parents.models import Parent



class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    classroom = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL, null=True, blank=True)
    house = models.ForeignKey(House, on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey(Parent, on_delete=models.SET_NULL, null=True, blank=True, related_name="children")
    admission_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    admission_date = models.DateField(max_length=50, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)

    def save(self, *args, **kwargs):

        if not self.admission_number:
            year = timezone.now().year

            last_student = Student.objects.filter(
                admission_number__startswith=f"JNV-{year}"
            ).order_by('id').last()

            if last_student:
                last_number = int(last_student.admission_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1

            self.admission_number = f"JNV-{year}-{str(new_number).zfill(5)}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.admission_number}"

