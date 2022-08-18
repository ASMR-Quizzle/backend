from django.urls import path

from .views import RewardsAPI, UserRegistrationAPI, UserEligibleTopicsAPI


urlpatterns = [
    path("register", UserRegistrationAPI.as_view(), name="user-register"),
    path("rewards", RewardsAPI.as_view(), name="user-rewards"),
    path("topics", UserEligibleTopicsAPI.as_view(), name="user eligible topics"),
]
