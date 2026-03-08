from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Create initial principal superuser"

    def handle(self, *args, **kwargs):
        username = "principal"
        password = "principal123"

        if not User.objects.filter(username=username).exists():
            user = User.objects.create_superuser(
                username=username,
                password=password,
                email="principal@school.com",
                role = "principal",
                gender = "male"
            )

            # user.is_staff = True
            # user.is_superuser = True
            user.save()

            self.stdout.write(self.style.SUCCESS("Principal superuser created"))
        else:
            self.stdout.write("Principal already exists") 