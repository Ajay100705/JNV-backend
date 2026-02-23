from django.db import models
from utils.choices import CLASS, SECTION

class ClassRoom(models.Model):
    class_name = models.CharField(max_length=10, choices=CLASS)
    section = models.CharField(max_length=1, choices=SECTION)

    def __str__(self):
        return f"{self.class_name} {self.section}"

