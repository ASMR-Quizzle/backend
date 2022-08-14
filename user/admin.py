from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Reward
from django.contrib.auth import get_user_model

User = get_user_model()

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Reward)
