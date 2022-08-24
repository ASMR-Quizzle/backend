from django.urls import path
from .views import InstituteRegistrationAPI

urlpatterns = [
     path("register",InstituteRegistrationAPI.as_view(),name = "institute registration ")
]
