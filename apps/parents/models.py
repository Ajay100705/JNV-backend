from django.db import models


class Parent(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    job = models.CharField(max_length=100, blank=True, null=True)

    phone1 = models.CharField(max_length=15)
    phone2 = models.CharField(max_length=15, blank=True, null=True)

    email = models.EmailField()

    photo = models.ImageField(upload_to='parent_photos/', blank=True, null=True)

    present_address = models.TextField()
    permanent_address = models.TextField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
