from django.db import models
from utils.choices import HOUSE, HOUSE_CATEGORY


class House(models.Model):
    house_name = models.CharField(max_length=20, choices=HOUSE)
    house_category = models.CharField(max_length=20, choices=HOUSE_CATEGORY)

    def __str__(self):
        return self.house_name
