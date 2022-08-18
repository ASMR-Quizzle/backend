from django.db import models
from django.db.models import CASCADE
from user.models import AppUser


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
    STATUS_CHOICES = (
        ("NOT REVIEWED", "NOT REVIEWED"),
        ("UNDER REVIEW", "UNDER REVIEW"),
        ("ACCEPTED", "ACCEPTED"),
        ("REJECTED", "REJECTED"),
    )
    setter = models.ForeignKey(
        AppUser, blank=False, null=False, on_delete=CASCADE, related_name="setter"
    )
    # reviewer = models.ForeignKey(
    #     AppUser, blank=True, null=True, on_delete=CASCADE, related_name="reviewer"
    # )
    reviewers = models.ManyToManyField(AppUser, related_name="reviewer")
    question = models.TextField()
    A = models.TextField(null=False, blank=False)
    B = models.TextField(null=False, blank=False)
    C = models.TextField(null=True, blank=True)
    D = models.TextField(null=True, blank=True)
    answer = models.CharField(max_length=1, choices=ANSWER_CHOICES)
    difficulty_score = models.FloatField(default=0)
    acceptance_score = models.FloatField(default=0)
    is_accepted = models.BooleanField(default=False)
    usage_score = models.IntegerField(default=0)
    topic = models.ForeignKey(Topic, blank=False, null=False, on_delete=CASCADE)
    reviews = models.IntegerField(default=0)
    status = models.CharField(
        max_length=256, choices=STATUS_CHOICES, default="NOT REVIEWED"
    )

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def __str__(self):
        return self.question


class UserEligibilityTest(models.Model):
    TEST_TYPE_CHOICES = (("SETTER", "SETTER"), ("REVIEWER", "REVIEWER"))
    appuser = models.ForeignKey(AppUser, null=False, blank=False, on_delete=CASCADE)
    topic = models.ForeignKey(Topic, blank=False, null=False, on_delete=CASCADE)
    test_type = models.CharField(
        max_length=20, choices=TEST_TYPE_CHOICES, default="SETTER"
    )
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=100)
    is_eligible = models.BooleanField(default=False)

    def __str__(self):
        return self.appuser.username + "_" + self.topic.name + "_" + self.test_type
