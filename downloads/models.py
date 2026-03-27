from django.db import models

from files.models import File
from organizations.models import Organization


class Download(models.Model):
    id = models.BigAutoField(primary_key=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)
    file = models.ForeignKey(File, related_name='downloads', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', related_name='downloads', on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, related_name='downloads', on_delete=models.CASCADE)

    class Meta:
        ordering = ['downloaded_at']

    def __str__(self):
        return f"{self.user} downloaded {self.file} at {self.downloaded_at}"
