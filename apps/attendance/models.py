from django.db import models
from django.conf import settings
from apps.students.models import Student
from apps.houses.models import House


class HouseAttendance(models.Model):

    STATUS_CHOICES = [
        ("present", "Present"),
        ("leave", "Leave"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="house_attendance"
    )

    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name="house_attendance"
    )

    date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="present"
    )

    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.student} - {self.house} - {self.date} - {self.status}"