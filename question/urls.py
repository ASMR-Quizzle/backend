from django.urls import path, include
from rest_framework import routers
from question.views import ReviewedQuestionsAPI, TranslateQuestionAPI

from .views import (
    CSVTestQuestions,
    MLModelPredictionAPI,
    QuestionBankGeneratorAPI,
    ReviewQuestionAPI,
    SetQuestionAPI,
    TopicsAPI,
    UploadCSV,
    UploadCSVAsync,
    UserEligibilityTestAPI,
    UserEligibilityTestTrackerAPI,
    TranslateAPI,
)

router = routers.SimpleRouter()
router.register(r"reviewer", ReviewedQuestionsAPI)
router.register(r"translate", TranslateQuestionAPI)

urlpatterns = [
    path("set", SetQuestionAPI.as_view(), name="set question"),
    path("uet", UserEligibilityTestAPI.as_view(), name="user eligibility test"),
    path(
        "uet/tracker", UserEligibilityTestTrackerAPI.as_view(), name="start uet tracker"
    ),
    path("review", ReviewQuestionAPI.as_view(), name="review questions"),
    path("topics", TopicsAPI.as_view(), name="all topics"),
    path("bulk/async", UploadCSVAsync.as_view(), name="bulk upload async"),
    path("bulk", UploadCSV.as_view(), name="bulk upload"),
    path("test", CSVTestQuestions.as_view(), name="test questions"),
    path("bank", QuestionBankGeneratorAPI.as_view(), name="question bank"),
    path("predict", MLModelPredictionAPI.as_view(), name="ml model prediction"),
    path("translate/<int:pk>", TranslateAPI.as_view(), name="translate"),
    path("", include(router.urls)),
]
