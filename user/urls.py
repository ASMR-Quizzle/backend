from django.urls import path, include

from .views import UserRegistrationAPI


urlpatterns = [
    path("register", UserRegistrationAPI.as_view(), name="user-register"),
]
