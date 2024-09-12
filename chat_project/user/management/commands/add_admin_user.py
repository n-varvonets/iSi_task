import os
from django.contrib.auth.hashers import make_password
from django.contrib.auth.management.commands import createsuperuser
from user.models import User


class Command(createsuperuser.Command):
    """
    A custom Django management command to create a superuser.

    python manage.py add_admin_user
    """
    def handle(self, *args, **options):
        first_name = "first_name_admin"
        last_name = "last_name_admin"
        username = "admin"
        email = "nickolay.varvonets@gmail.com"

        email = os.getenv("ADMIN_EMAIL", email)
        password = os.getenv("ADMIN_PASSWORD", "1qwerty2")
        if not password or not email:
            raise Exception("Email or password are not provided.")

        user = User.objects.create_superuser(
            email=email.lower(),
            password=password,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
        )

        return f"Admin({user.email}) was added"
