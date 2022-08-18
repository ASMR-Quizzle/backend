from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.response import Response

from .serializers import (
    ReviewQuestionSerializer,
    SetQuestionSerializer,
    TopicSerializer,
    UserEligibilityTestSerializer,
)
from .models import Question, Topic, UserEligibilityTest


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
            topic_list = []
            topics = questions_queryset[i].topics.all()
            for topic in topics:
                topic_list.append(topic.name)
            questions[i]["topics"] = topic_list
            questions[i]["reviewers"] = reviewer_list
        return Response({"data": questions})

    def post(self, request, *args, **kwargs):
        user = request.user
        appUser = user.appuser
        if appUser.is_setter == False:
            return Response(status=400, data={"error": "user not a question setter"})
        topics = request.data["topics"]
        topics_queryset = []
        for topic in topics:
            if not Topic.objects.filter(name=topic).exists():
                return Response(
                    status=404,
                    data={"error": f"Topic '{request.data['topic']}' does not exist"},
                )
            else:
                topics_queryset.append(Topic.objects.get(name=topic))
        for topic in topics_queryset:
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
        )
        question.save()
        for topic in topics_queryset:
            topic.question_count += 1
            topic.save()
            question.topics.add(topic)
        question.save()
        return Response({"message": "Quesiton created successfully"})


class UserEligibilityTestAPI(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserEligibilityTestSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        appUser = user.appuser
        test_type = request.data["test_type"]
        score = request.data["score"]
        max_score = request.data["max_score"]

        if appUser.is_setter == False and request.data["test_type"] == "SETTER":
            return Response(status=400, data={"error": "user not a question setter"})

        if appUser.is_reviewer == False and request.data["test_type"] == "REVIEWER":
            return Response(
                status=400, data={"error": "user is not a question reviewer"}
            )

        if not Topic.objects.filter(name=request.data["topic"]).exists():
            return Response(
                status=404,
                data={"error": f"Topic '{request.data['topic']}' does not exist"},
            )
        topic = Topic.objects.get(name=request.data["topic"])
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
                    "data": {
                        "is_eligible": is_eligible,
                        "topic": topic.name,
                        "test_type": test_type,
                    },
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
                "data": {
                    "is_eligible": is_eligible,
                    "topic": topic.name,
                    "test_type": test_type,
                },
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
        for i in range(len(uet_eligible)):
            topic_list.append(Topic.objects.get(pk=uet_eligible[i]["topic_id"]))

        # temporary arrangement
        questions_queryset = (
            Question.objects.all()
            .exclude(setter=appUser)
            .exclude(reviewers__in=[appUser])
            .exclude(reviews=3)
            .filter(is_accepted=False)
            .filter(topics__in=topic_list)
        )
        questions = questions_queryset.values()

        for i in range(len(questions)):
            reviewer_list = []
            reviewers = questions_queryset[i].reviewers.all()
            for reviewer in reviewers:
                reviewer_list.append(reviewer.username)
            topic_list = []
            topics = questions_queryset[i].topics.all()
            for topic in topics:
                topic_list.append(topic.name)
            questions[i]["topics"] = topic_list
            # questions[i]["topic"] = Topic.objects.get(pk=questions[i]["topic_id"]).name
            questions[i]["reviewers"] = reviewer_list
        return Response({"data": questions})

    def post(self, request, *args, **kwargs):
        user = request.user
        appUser = user.appuser
        if appUser.is_reviewer == False:
            return Response(status=400, data={"error": "user not a question reviewer"})
        question_id = request.data["id"]
        question = Question.objects.get(pk=question_id)
        for reviewer in question.reviewers.all():
            if appUser.username == reviewer.username:
                return Response(
                    data={"error": "user has already reviewed this question"},
                    status=400,
                )
        topics = question.topics.all()
        for topic in topics:
            if not UserEligibilityTest.objects.filter(
                topic__in=topics,
                appuser=appUser,
                test_type="REVIEWER",
            ).exists():
                return Response(
                    status=400,
                    data={"error": "User not eligible to review this question"},
                )
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
        else:
            reviewers = question.reviewers.all()
            for reviewer in reviewers:
                reviewer_list.append(reviewer.username)
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


class TopicsAPI(generics.GenericAPIView):
    serializer_class = TopicSerializer

    def get(self, request, *args, **kwargs):
        topics = Topic.objects.all().values()
        return Response(data={"data": topics})
