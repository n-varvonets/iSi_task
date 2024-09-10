from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.utils.translation import gettext_lazy as _

__all__ = (
    "User"
)


class User(AbstractBaseUser, PermissionsMixin):
    USER = 1
    ADMIN = 2

    ROLE_CHOICES = (
        (USER, "User"),
        (ADMIN, "Admin"),
    )

    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=USER)
    email = models.EmailField(max_length=255, null=False,
                              unique=True, db_index=True)

    first_name = models.CharField(max_length=124, null=True, blank=True)
    last_name = models.CharField(max_length=124, null=True, blank=True)
    avatar = models.URLField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    objects = UserManager()
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"  # auth by email, not username

