from django.urls import path, include

from .views import ReviewQuestionAPI, SetQuestionAPI, UserEligibilityTestAPI


urlpatterns = [
    path("set", SetQuestionAPI.as_view(), name="set question"),
    path("uet", UserEligibilityTestAPI.as_view(), name="user eligibility test"),
    path("review", ReviewQuestionAPI.as_view(), name="review questions"),
]
