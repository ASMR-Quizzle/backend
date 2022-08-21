from pydoc_data.topics import topics
from rest_framework import serializers

from .models import Question


class SetQuestionSerializer(serializers.Serializer):
    question = serializers.CharField()
    A = serializers.CharField()
    B = serializers.CharField()
    C = serializers.CharField()
    D = serializers.CharField()
    answer = serializers.CharField()
    difficulty_score = serializers.FloatField()
    topics = serializers.CharField()
    explanation = serializers.CharField()


class UserEligibilityTestSerializer(serializers.Serializer):
    test_type = serializers.CharField(max_length=256)
    topic = serializers.CharField()
    score = serializers.IntegerField()
    max_score = serializers.IntegerField()


class ReviewQuestionSerializer(serializers.Serializer):
    difficulty_score = serializers.FloatField()
    acceptance_score = serializers.FloatField()
    id = serializers.CharField()
    topic_id = serializers.CharField()


class TopicSerializer(serializers.Serializer):
    pass


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    class Meta:
        fields = ("file",)


class CSVTestQuestionsSerializer(serializers.Serializer):
    pass


class CSVTestQuestionsQuerySerializer(serializers.Serializer):
    topic = serializers.CharField(max_length=512)
    type = serializers.CharField(max_length=512)
    limit = serializers.CharField(max_length=512)


class UserEligibilityTestTrackerSerializer(serializers.Serializer):
    topic = serializers.CharField(max_length=512)
    test_type = serializers.CharField(max_length=512)
    duration = serializers.IntegerField()


class QuestionBankGeneratorQuerySerializer(serializers.Serializer):
    topics = serializers.CharField()
    easy = serializers.CharField()
    medium = serializers.CharField()
    hard = serializers.CharField()
    type = serializers.CharField()


class QuestionBankGeneratorSerializer(serializers.Serializer):
    pass
