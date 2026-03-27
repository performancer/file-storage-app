from django.db import models

# Create your models here.

class File(models.Model):
    id = models.BigAutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=256)

    class Meta:
        ordering = ['created']