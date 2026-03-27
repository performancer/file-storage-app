from django.contrib.auth.models import User
from django.db import models

from organizations.models import Organization

class OrganizationUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
