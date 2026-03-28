from django.db import models

from file_storage_app import settings
from files.models import File
from organizations.models import Organization


class Download(models.Model):
    id = models.BigAutoField(primary_key=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)
    file = models.ForeignKey(File, related_name='downloads', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='downloads', on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, related_name='downloads', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-downloaded_at']  # latest first

    def __str__(self):
        return f"{self.user} downloaded {self.file} at {self.downloaded_at}"
