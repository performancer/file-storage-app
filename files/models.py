import uuid

from django.db import models

from organizations.models import Organization


def upload_path(instance, filename: str) -> str:
    ext = filename.split('.')[-1]
    return f'media/organizations/{instance.organization.id}/{instance.owner.id}/{uuid.uuid4()}.{ext}'


class File(models.Model):
    id = models.BigAutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=upload_path)
    owner = models.ForeignKey('auth.User', related_name='files', on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, related_name='files', on_delete=models.CASCADE)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f"{self.file}"