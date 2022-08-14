from django.db import models
from django.db.models import CASCADE
from django.contrib.auth import get_user_model

User = get_user_model()

class Topic(models.Model):
    class Meta:
        verbose_name = "Topic"
        verbose_name_plural = "Topics"

    name = models.CharField(max_length=256, null=False, blank=False)
    question_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Question(models.Model):
    ANSWER_CHOICES = (
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
    )
    setter = models.ForeignKey(
        User, blank=False, null=False, on_delete=CASCADE, related_name="setter"
    )
    reviewer = models.ForeignKey(
        User, blank=True, null=True, on_delete=CASCADE, related_name="reviewer"
    )
    question = models.TextField()
    A = models.TextField()
    B = models.TextField()
    C = models.TextField()
    D = models.TextField()
    answer = models.CharField(max_length=1, choices=ANSWER_CHOICES)
    difficulty_score = models.FloatField()
    acceptance_score = models.FloatField()
    is_accepted = models.BooleanField()
    usage_score = models.IntegerField()
    topic = models.ForeignKey(Topic, blank=False, null=False, on_delete=CASCADE)

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def __str__(self):
        return self.name


class UserEligibilityTest(models.Model):
    TEST_TYPE_CHOICES = (
        ("SETTER", "SETTER"), 
        ("REVIEWER", "REVIEWER")
    )
    appuser = models.ForeignKey(User, null=False, blank=False, on_delete=CASCADE)
    topic = models.ForeignKey(Topic, blank=False, null=False, on_delete=CASCADE)
    test_score = models.CharField(
        max_length=20, choices=TEST_TYPE_CHOICES, default="SETTER"
    )
    score = models.IntegerField(default=0)
    max_score = models.IntegerField()
    is_eligible = models.BooleanField(default=False)
