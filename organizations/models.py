from django.contrib.auth.models import User
from django.db import models

class Organization(models.Model):
    id = models.BigAutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name
