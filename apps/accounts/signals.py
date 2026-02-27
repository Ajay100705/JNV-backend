from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, PrincipalProfile


@receiver(post_save, sender=User)
def create_principal_profile(sender, instance, created, **kwargs):
    if created and instance.role == "principal":
        PrincipalProfile.objects.create(user=instance)