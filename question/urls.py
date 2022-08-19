from django.urls import path

from .views import (
    CSVTestQuestions,
    ReviewQuestionAPI,
    SetQuestionAPI,
    TopicsAPI,
    UploadCSV,
    UserEligibilityTestAPI,
    UserEligibilityTestTrackerAPI,
)


urlpatterns = [
    path("set", SetQuestionAPI.as_view(), name="set question"),
    path("uet", UserEligibilityTestAPI.as_view(), name="user eligibility test"),
    path(
        "uet/tracker", UserEligibilityTestTrackerAPI.as_view(), name="start uet tracker"
    ),
    path("review", ReviewQuestionAPI.as_view(), name="review questions"),
    path("topics", TopicsAPI.as_view(), name="all topics"),
    path("bulk", UploadCSV.as_view(), name="bulk upload"),
    path("test", CSVTestQuestions.as_view(), name="test questions"),
]
