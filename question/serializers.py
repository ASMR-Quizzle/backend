from pyexpat import model
from rest_framework import serializers
from djoser.serializers import UserSerializer
from question.models import Question, Topic, UserEligibilityTest

class TopicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Topic
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    setter = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    topic = TopicSerializer(read_only=True)

    class Meta:
        model = Question
        fields = '__all__'

class UserEligibilityTestSerializer(serializers.ModelSerializer):
    appuser = UserSerializer(read_only=True)
    topic = TopicSerializer(read_only=True)

    class Meta:
        model = UserEligibilityTest
        fields = '__all__'