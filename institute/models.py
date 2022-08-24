from django.db import models

from django.contrib.auth.models import User
from django.db.models import CASCADE

# Create your models here.


class Institute(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=CASCADE)
    name = models.CharField(max_length=256)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=64, blank=True, null=True)
    username = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Institute"
        verbose_name_plural = "Institutes"

    def __str__(self):
        return self.name
