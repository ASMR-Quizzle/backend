from django.urls import path, include
from rest_framework import routers
from .views import RewardsAPI, UserRegistrationAPI, UserEligibleTopicsAPI, UserAPI

router = routers.SimpleRouter()
router.register(r'', UserAPI, basename='user')

urlpatterns = [
    path("register", UserRegistrationAPI.as_view(), name="user-register"),
    path("rewards", RewardsAPI.as_view(), name="user-rewards"),
    path("topics", UserEligibleTopicsAPI.as_view(), name="user eligible topics"),
    path('', include(router.urls)),
]
