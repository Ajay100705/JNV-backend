from django.db import models
from django.forms import ValidationError
from utils.choices import HOUSE, HOUSE_CATEGORY
from apps.teachers.models import TeacherProfile


class House(models.Model):
    house_name = models.CharField(max_length=20, choices=HOUSE)
    house_category = models.CharField(max_length=20, choices=HOUSE_CATEGORY)

    def __str__(self):
        return self.house_name

class HouseMaster(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    is_house_master = models.BooleanField(default=False)

    class Meta:
        unique_together = ('teacher', 'house')

    def clean(self):
        if self.house_id:
            if HouseMaster.objects.filter(house_id=self.house_id).exclude(pk=self.pk).count() >= 2:
                raise ValidationError("Only 2 teachers allowed per house")

    def save(self, *args, **kwargs):
        self.full_clean()   # THIS safely calls clean()
        super().save(*args, **kwargs)