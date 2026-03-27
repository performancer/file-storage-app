from django.db import models


class File(models.Model):
    id = models.BigAutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=256)
    owner = models.ForeignKey('auth.User', related_name='files', on_delete=models.CASCADE)

    class Meta:
        ordering = ['created']
