from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

from file_storage_app import settings
from organizations.models import Organization


# as we have overridden the built-in user, and we require all users to be in an organization
# we are going to also override the user manager to ensure organization requirement is fulfilled
# and that superusers can be made even when there are no organizations existing
class UserManager(BaseUserManager):
    def create_user(self, username, password=None, organization=None, **extra_fields):
        if not username:
            raise ValueError('Users must have a username')

        if not organization:
            raise ValueError('Users must have a organization')

        user = self.model(username=username, organization=organization, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # let's create a default organization for now, they can edit that stuff later
        organization, _ = Organization.objects.get_or_create(name=settings.DEFAULT_ORGANIZATION_NAME)

        return self.create_user(
            username=username,
            password=password,
            organization=organization,
            **extra_fields
        )


# this is the actual override for the user
class User(AbstractUser):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="users",
        null=False,  # all users must belong to an org
        blank=False,
    )

    objects = UserManager()
