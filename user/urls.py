from django.urls import path, include
from rest_framework import routers
import user.views as views

router = routers.DefaultRouter()

urlpatterns = [
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
    path("", include(router.urls)),
]
