import datetime
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.response import Response
import pandas as pd
from drf_yasg.utils import swagger_auto_schema
from question.tasks import ml_model_prediction_task, uploadCSVTask
from user.models import AppUser
import pytz
import pickle
from .serializers import (
    CSVTestQuestionsQuerySerializer,
    CSVTestQuestionsSerializer,
    FileUploadSerializer,
    QuestionBankGeneratorQuerySerializer,
    QuestionBankGeneratorSerializer,
    ReviewQuestionSerializer,
    SetQuestionSerializer,
    TopicSerializer,
    UserEligibilityTestSerializer,
    UserEligibilityTestTrackerSerializer,
)
from .models import (
    CSVFile,
    Question,
    Topic,
    UserEligibilityTest,
    UserEligibilityTestTracker,
)
import torch
from torch import nn
from transformers import AutoTokenizer, AutoModel
from ml_collections import ConfigDict
import numpy as np

cfg = ConfigDict()
cfg.epochs = 10
cfg.max_length = 256
cfg.batch_size = 32


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
        explanation = request.data["explanation"]
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
            explanation=explanation,
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

        if not Topic.objects.filter(name=request.data["topic"]).exists():
            return Response(
                status=404,
                data={"error": f"Topic '{request.data['topic']}' does not exist"},
            )
        topic = Topic.objects.get(name=request.data["topic"])
        is_eligible = score >= 35
        if is_eligible:
            if request.data["test_type"] == "REVIEWER" and appUser.is_reviewer == False:
                appUser.is_reviewer = True
                appUser.save()

            if request.data["test_type"] == "SETTER" and appUser.is_setter == False:
                appUser.is_setter = True
                appUser.save()

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


class UploadCSV(generics.GenericAPIView):
    serializer_class = FileUploadSerializer
    premission_classes = IsAuthenticated

    def post(self, request, *args, **kwargs):
        if request.user.is_superuser == False:
            return Response(status=401, data={"error": "Admins only route"})
        if not AppUser.objects.filter(user=request.user).exists():
            return Response(
                status=400, data={"error": "No App User associated with current admin"}
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data["file"]
        reader = pd.read_csv(file)
        question_count = 0
        saved_count = 0
        for _, row in reader.iterrows():
            question_count += 1
            question = row["Question"]
            A = row["A"]
            B = row["B"]
            C = row["C"]
            D = row["D"]
            answer = row["Answer"]
            topic_name = row["Topic"]
            explanation = row["Explanation"]
            difficulty_score = row["Difficulty"]
            if not (
                A
                or B
                or C
                or D
                or answer
                or question
                or topic
                or explanation
                or difficulty_score
            ):
                continue
            if not Topic.objects.filter(name=topic_name).exists():
                topic = Topic(name=topic_name)
                topic.save()
            topic = Topic.objects.get(name=topic_name)
            topic.question_count += 1
            new_question = Question(
                setter=request.user.appuser,
                question=question,
                A=A,
                B=B,
                C=C,
                D=D,
                answer=answer,
                difficulty_score=difficulty_score,
                acceptance_score=75,
                is_accepted=True,
                status="ACCEPTED",
                reviews=3,
                explanation=explanation,
            )
            new_question.save()
            new_question.topics.add(topic)
            new_question.reviewers.add(request.user.appuser)
            new_question.save()
            saved_count += 1

        return Response(
            status=201,
            data={
                "data": {
                    "total_questions": question_count,
                    "successful_uploads": saved_count,
                }
            },
        )


class CSVTestQuestions(generics.GenericAPIView):
    serializer_class = CSVTestQuestionsSerializer

    @swagger_auto_schema(
        query_serializer=CSVTestQuestionsQuerySerializer,
        security=[],
        operation_id="Get Test Data",
        operation_description="This endpoint is used to get accepted questions for a particular topic, type can be assigned as csv if csv is expected as response else json data is returned by default",
    )
    def get(self, request, *args, **kwargs):
        limit = request.GET.get("limit")
        if limit is None:
            limit = 5
        format = request.GET.get("type")
        topic_name = request.GET.get("topic")
        if not Topic.objects.filter(name=topic_name).exists():
            return Response(
                status=404, data={"error": f"Topic '{topic_name}' does not exist"}
            )
        topic = Topic.objects.get(name=topic_name)
        questions = list(
            Question.objects.filter(topics__in=[topic], is_accepted=True).values()
        )[: int(limit)]

        if format == "csv":
            df = pd.DataFrame(
                columns=[
                    "Question",
                    "A",
                    "B",
                    "C",
                    "D",
                    "Answer",
                ]
            )
            for question in questions:
                df.loc[len(df.index)] = [
                    question["question"],
                    question["A"],
                    question["B"],
                    question["C"],
                    question["D"],
                    question["answer"],
                ]
            response = HttpResponse(content_type="text/csv")
            response[
                "Content-Disposition"
            ] = f"attachment; filename={topic_name}_{limit}_Questions.csv"
            df.to_csv(
                path_or_buf=response,
                sep=";",
                float_format="%.2f",
                index=False,
                decimal=",",
            )
            return response
        return Response(data={"data": questions})


class UserEligibilityTestTrackerAPI(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserEligibilityTestTrackerSerializer

    def post(self, request, *args, **kwargs):
        appuser = request.user.appuser
        test_type = request.data["test_type"]
        duration = int(request.data["duration"])  # in hours
        topic_name = request.data["topic"]
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(hours=duration)

        if UserEligibilityTestTracker.objects.filter(
            has_ended=False, appuser=appuser
        ).exists():
            return Response(
                data={"error": "User is already enrolled in one active test"},
                status=400,
            )

        topic = Topic.objects.get(name=topic_name)

        uet_tracker = UserEligibilityTestTracker(
            start_time=start_time,
            end_time=end_time,
            has_ended=(start_time == end_time),
            appuser=appuser,
            topic=topic,
            test_type=test_type,
            duration=duration,
        )
        uet_tracker.save()
        return Response(
            data={
                "data": {
                    "tracker_id": uet_tracker.pk,
                    "start_time": start_time,
                    "end_time": end_time,
                    "topic": topic_name,
                    "duration": duration,
                    "test_type": test_type,
                    "has_ended": False,
                }
            }
        )

    def get(self, request, *args, **kwargs):
        appuser = request.user.appuser
        if not UserEligibilityTestTracker.objects.filter(
            has_ended=False, appuser=appuser
        ).exists():
            return Response(
                data={"error": "User not enrolled in any test at this moment"},
                status=400,
            )
        utc = pytz.UTC
        uet_tracker = UserEligibilityTestTracker.objects.get(
            has_ended=False, appuser=appuser
        )
        current_time = utc.localize(datetime.datetime.now())
        end_time = uet_tracker.end_time
        if end_time <= current_time:
            uet_tracker.has_ended = True
            uet_tracker.save()
        return Response(
            data={
                "data": {
                    "tracker_id": uet_tracker.pk,
                    "start_time": uet_tracker.start_time,
                    "end_time": uet_tracker.end_time,
                    "topic": uet_tracker.topic.name,
                    "duration": uet_tracker.duration,
                    "test_type": uet_tracker.test_type,
                    "has_ended": uet_tracker.has_ended,
                }
            }
        )


class QuestionBankGeneratorAPI(generics.GenericAPIView):
    serializer_class = QuestionBankGeneratorSerializer

    @swagger_auto_schema(
        query_serializer=QuestionBankGeneratorQuerySerializer,
        security=[],
        operation_id="Get Test Data as CSV",
        operation_description="This endpoint is used to get accepted questions for a particular topic, type can be assigned as csv if csv is expected as response else json data is returned by default",
    )
    def get(self, request, *args, **kwargs):
        topic_names = request.GET.get("topics").split("+")[0].split(" ")
        easy = request.GET.get("easy").split("+")[0].split(" ")
        medium = request.GET.get("medium").split("+")[0].split(" ")
        hard = request.GET.get("hard").split("+")[0].split(" ")
        format = request.GET.get("type")
        topics = Topic.objects.all().filter(name__in=topic_names)
        questions_queryset = Question.objects.all().filter(
            topics__in=topics, is_accepted=True
        )
        questions = []
        for i in range(len(topic_names)):
            easy[i] = int(easy[i])
            medium[i] = int(medium[i])
            hard[i] = int(hard[i])
        for i in range(len(topics)):
            sub_query = questions_queryset.filter(topics__in=[topics[i]])
            sub_query_easy = list(
                sub_query.filter(
                    difficulty_score__gte=0, difficulty_score__lte=33
                ).values()
            )[: easy[i]]
            sub_query_medium = list(
                sub_query.filter(
                    difficulty_score__gte=34, difficulty_score__lte=66
                ).values()
            )[: medium[i]]
            sub_query_hard = list(
                sub_query.filter(
                    difficulty_score__gte=67, difficulty_score__lte=100
                ).values()
            )[: hard[i]]
            questions += sub_query_easy
            questions += sub_query_medium
            questions += sub_query_hard

        if format == "csv":
            df = pd.DataFrame(
                columns=[
                    "Question",
                    "A",
                    "B",
                    "C",
                    "D",
                    "Answer",
                    "Explanation",
                    "Difficulty",
                ]
            )
            for question in questions:
                print(question)
                df.loc[len(df.index)] = [
                    question["question"],
                    question["A"],
                    question["B"],
                    question["C"],
                    question["D"],
                    question["answer"],
                    question["explanation"],
                    question["difficulty_score"],
                ]
            response = HttpResponse(content_type="text/csv")
            response[
                "Content-Disposition"
            ] = f"attachment; filename=Quizzle_Questions.csv"
            df.to_csv(
                path_or_buf=response,
                sep=";",
                float_format="%.2f",
                index=False,
                decimal=",",
            )
            return response
        return Response(data={"data": questions})


class UploadCSVAsync(generics.GenericAPIView):
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        if request.user.is_superuser == False:
            return Response(status=401, data={"error": "Admins only route"})
        if not AppUser.objects.filter(user=request.user).exists():
            return Response(
                status=400, data={"error": "No App User associated with current admin"}
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data["file"]
        csv = CSVFile(file=file)
        csv.save()
        task = uploadCSVTask.delay(csv.pk, request.user.appuser.pk)
        return Response(data={"task_id": str(task)})


class MLModelPredictionAsyncAPI(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        task = ml_model_prediction_task.delay("What are the worst mammals?")
        return Response(data={"task_id": task.id})


class Classifier(nn.Module):
    def __init__(self, label_to_int, model_alias=None, cfg=None):
        super().__init__()
        if model_alias is not None:
            self.backbone = AutoModel.from_pretrained(model_alias)
            self.tokenizer = AutoTokenizer.from_pretrained(model_alias)
        else:
            self.backbone = AutoModel.from_pretrained("roberta-base")
            self.tokenizer = AutoTokenizer.from_pretrained("roberta-base")

        self.lin = nn.Linear(768, len(label_to_int.keys()))
        self.device = torch.device("cpu")

        self.cfg = cfg

    def forward(self, batch):
        tokenized = self.tokenizer(
            text=list(batch[0]),
            return_attention_mask=True,
            max_length=cfg.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        tokenized = {k: v.to(self.device) for k, v in tokenized.items()}
        x = self.backbone(**tokenized)
        x = self.lin(x.pooler_output)
        return x


class MLModelPredictionAPI(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        # filename = "roberta10_model_classification.sav"
        # loaded_model = pickle.load(open(filename, "rb"))
        # result = loaded_model.predict(["What is the point of life?"])
        # topics = ["Physics", "Chemistry", "Maths", "Biology"]
        # return Response(data={"topic": topics[result[0][0]]})
        category_mapping = {"P": 0, "C": 1, "M": 2, "B": 3}
        print("e")
        device = torch.device("cpu")
        model = Classifier(category_mapping)
        model.load_state_dict(torch.load("topic_weights.pt", map_location=device))
        with torch.no_grad():
            model.eval()
            output = model([["What are aromatic compounds?"]])
        reverse_list = ["Physics", "Chemistry", "Maths", "Biology"]
        topic = reverse_list[int(np.argmax(output))]
        print(topic)
        return Response(data={"data": topic})
