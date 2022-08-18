from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.response import Response

from .serializers import (
    ReviewQuestionSerializer,
    SetQuestionSerializer,
    UserEligibilityTestSerializer,
)
from .models import Question, Topic, UserEligibilityTest

# Create your views here.
class SetQuestionAPI(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SetQuestionSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        appUser = user.appuser
        if appUser.is_setter == False:
            return Response(status=400, data={"error": "user not a question setter"})
        questions_queryset = Question.objects.all().filter(setter=appUser)
        questions = questions_queryset.values()
        for i in range(len(questions)):
            reviewer_list = []
            reviewers = questions_queryset[i].reviewers.all()
            for reviewer in reviewers:
                reviewer_list.append(reviewer.username)
            questions[i]["topic"] = Topic.objects.get(pk=questions[i]["topic_id"]).name
            questions[i]["reviewers"] = reviewer_list

        return Response({"data": questions})

    def post(self, request, *args, **kwargs):
        user = request.user
        appUser = user.appuser
        if appUser.is_setter == False:
            return Response(status=400, data={"error": "user not a question setter"})
        topic = Topic.objects.get(name=request.data["topic"])
        uet = UserEligibilityTest.objects.all().filter(
            topic=topic, appuser=appUser, test_type="SETTER", is_eligible=True
        )
        if len(uet) == 0:
            return Response(
                status=400,
                data={
                    "error": f"user not eligible to set questions for topic: {topic.name}"
                },
            )
        content = request.data["question"]
        A = request.data["A"]
        B = request.data["B"]
        C = request.data["C"]
        D = request.data["D"]
        answer = request.data["answer"]
        difficulty_score = request.data["difficulty_score"]
        question = Question(
            setter=appUser,
            question=content,
            A=A,
            B=B,
            C=C,
            D=D,
            answer=answer,
            difficulty_score=difficulty_score,
            topic=topic,
        )
        question.save()
        return Response({"message": "Quesiton created successfully"})


class UserEligibilityTestAPI(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserEligibilityTestSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        appUser = user.appuser
        if appUser.is_setter == False and request.data["test_type"] == "SETTER":
            return Response(status=400, data={"error": "user not a question setter"})

        if appUser.is_reviewer == False and request.data["test_type"] == "REVIEWER":
            return Response(status=400, data={"error": "user not a question reviewer"})
        test_type = request.data["test_type"]
        topic = Topic.objects.get(name=request.data["topic"])
        score = request.data["score"]
        max_score = request.data["max_score"]
        is_eligible = score >= 35
        if UserEligibilityTest.objects.filter(
            topic=topic, appuser=appUser, test_type=test_type
        ).exists():
            user_eligibility_test = UserEligibilityTest.objects.get(
                topic=topic, appuser=appUser, test_type=test_type
            )
            user_eligibility_test.is_eligible = is_eligible
            user_eligibility_test.score = score
            user_eligibility_test.save()

            return Response(
                {
                    "message": "UET Report Updated Successfully",
                    "data": {"is_eligible": is_eligible},
                }
            )
        else:
            user_eligibility_test = UserEligibilityTest(
                appuser=appUser,
                topic=topic,
                score=score,
                test_type=test_type,
                is_eligible=is_eligible,
                max_score=max_score,
            )
            user_eligibility_test.save()
        return Response(
            {
                "message": "UET Report Generated Successfully",
                "data": {"is_eligible": is_eligible},
            }
        )


class ReviewQuestionAPI(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReviewQuestionSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        appUser = user.appuser
        if appUser.is_reviewer == False:
            return Response(status=400, data={"error": "user not a question reviewer"})
        uet_eligible = UserEligibilityTest.objects.filter(
            appuser=appUser, test_type="REVIEWER", is_eligible=True
        ).values()
        topic_list = []
        topic_id_list = []
        for i in range(len(uet_eligible)):
            topic_list.append(Topic.objects.get(pk=uet_eligible[i]["topic_id"]))
            topic_id_list.append(uet_eligible[i]["topic_id"])

        # temporary arrangement
        questions_queryset = (
            Question.objects.all()
            .exclude(setter=appUser)
            .exclude(reviewers__in=[appUser])
            .exclude(reviews=3)
            .filter(is_accepted=False)
            .filter(topic_id__in=topic_list)
        )
        questions = questions_queryset.values()

        for i in range(len(questions)):
            reviewer_list = []
            reviewers = questions_queryset[i].reviewers.all()
            for reviewer in reviewers:
                reviewer_list.append(reviewer.username)
            questions[i]["topic"] = Topic.objects.get(pk=questions[i]["topic_id"]).name
            questions[i]["reviewers"] = reviewer_list
        return Response({"data": questions})

    def post(self, request, *args, **kwargs):
        user = request.user
        appUser = user.appuser
        if appUser.is_reviewer == False:
            return Response(status=400, data={"error": "user not a question reviewer"})
        topic_id = request.data["topic_id"]
        question_id = request.data["id"]
        topic = Topic.objects.get(pk=topic_id)
        if not UserEligibilityTest.objects.filter(
            topic=topic,
            appuser=appUser,
            test_type="REVIEWER",
        ).exists():
            return Response(
                status=400, data={"error": "User not eligible to Review this question"}
            )
        question = Question.objects.get(pk=question_id)
        question.status = "UNDER REVIEW"
        if question.reviews >= 3:
            return Response(
                status=400, data={"error": "Max review limit reached for this question"}
            )

        if question.reviews != 0:
            acceptance_score = (
                question.acceptance_score + request.data["acceptance_score"]
            ) / 2
        else:
            acceptance_score = request.data["acceptance_score"]

        difficulty_score = (
            question.difficulty_score + request.data["difficulty_score"]
        ) / 2
        question.difficulty_score = difficulty_score
        question.acceptance_score = acceptance_score
        question.topic = topic
        question.reviewers.add(appUser)
        question.reviews += 1
        reviewer_list = []
        if question.reviews == 3:
            question.is_accepted = acceptance_score >= 35
            reviewers = question.reviewers.all()
            for reviewer in reviewers:
                reviewer_list.append(reviewer.username)
                if reviewer.reward is not None:
                    reviewer.reward.points += 3.5
                    reviewer.reward.save()
            setter = question.setter
            if setter.reward is not None and question.is_accepted:
                setter.reward.points += 8.5
                question.status = "ACCEPTED"
                setter.reward.save()
            else:
                question.status = "REJECTED"

        question.save()
        return Response(
            {
                "message": "question reviewed successfully",
                "question_approval_status": question.is_accepted,
                "question_acceptance_score": question.acceptance_score,
                "question_difficulty_score": question.difficulty_score,
                "reviewers": reviewer_list,
                "status": question.status,
            }
        )
