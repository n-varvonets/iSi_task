import base64
import os
from io import BytesIO

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.management.commands import createsuperuser
from django.core.mail import send_mail
from django.utils.html import strip_tags
from user.models import User


class Command(createsuperuser.Command):
    """
    A custom Django management command to create a superuser.

    python manage.py add_admin_user
    """

    def handle(self, *args, **options):

        print("Starting to create admin user")  # Отладочный вывод

        first_name = "first_name_admin"
        last_name = "last_name_admin"
        email = "nickolay.varvonets@gmail.com"

        email = os.getenv("ADMIN_EMAIL", email)
        password = os.getenv("ADMIN_PASSWORD", "1qwerty2")
        if not password or not email:
            raise Exception("Email or password are not provided.")

        user = User.objects.create(
            email=email.lower(),
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )

        return f"Admin({user.email}) was added"
