from django.db import models
from django.db.models import CASCADE
from django.contrib.auth.models import User


class Reward(models.Model):
    wallet_address = models.CharField(max_length=256)
    points = models.FloatField(default=float(0))

    class Meta:
        verbose_name = "Reward"
        verbose_name_plural = "Rewards"

    def __str__(self):
        return self.name


class AppUser(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=CASCADE)
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    is_setter = models.BooleanField()
    is_reviewer = models.BooleanField()
    questions_submitted = models.IntegerField(default=0)
    questions_accepted = models.IntegerField(default=0)
    questions_reviewed = models.IntegerField(default=0)
    questions_rejected = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)
    reward = models.OneToOneField(Reward, null=True, blank=True, on_delete=CASCADE)

    class Meta:
        verbose_name = "AppUser"
        verbose_name_plural = "AppUsers"

    def __str__(self):
        return self.username
