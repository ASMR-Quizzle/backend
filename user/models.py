from django.db import models
from django.db.models import CASCADE
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone  


class Reward(models.Model):
    wallet_address = models.CharField(max_length=256)
    points = models.FloatField(default=float(0))

    class Meta:
        verbose_name = "Reward"
        verbose_name_plural = "Rewards"

    def __str__(self):
        return self.name


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("User must have an email")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        user = self.create_user(username, email, password=password, **extra_fields)
        user.is_active = True
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)  
    # extra fields
    is_setter = models.BooleanField()
    is_reviewer = models.BooleanField()
    questions_submitted = models.IntegerField(default=0)
    questions_accepted = models.IntegerField(default=0)
    questions_reviewed = models.IntegerField(default=0)
    questions_rejected = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)
    reward = models.OneToOneField(
        Reward, 
        null=True, 
        blank=True, 
        on_delete=CASCADE
    )

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name", "is_setter", "is_reviewer"]

    def __str__(self):
        return str(self.email) + str(self.role)

    def get_full_name(self):
        return f"{self.first_name} - {self.last_name}"

    def get_short_name(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __str__(self):
        return self.email
