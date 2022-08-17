# Generated by Django 4.1 on 2022-08-17 06:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Topic",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=256)),
                ("question_count", models.IntegerField(default=0)),
            ],
            options={
                "verbose_name": "Topic",
                "verbose_name_plural": "Topics",
            },
        ),
        migrations.CreateModel(
            name="UserEligibilityTest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "test_score",
                    models.CharField(
                        choices=[("SETTER", "SETTER"), ("REVIEWER", "REVIEWER")],
                        default="SETTER",
                        max_length=20,
                    ),
                ),
                ("score", models.IntegerField(default=0)),
                ("max_score", models.IntegerField()),
                ("is_eligible", models.BooleanField(default=False)),
                (
                    "appuser",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="user.appuser"
                    ),
                ),
                (
                    "topic",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="question.topic"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("question", models.TextField()),
                ("A", models.TextField()),
                ("B", models.TextField()),
                ("C", models.TextField()),
                ("D", models.TextField()),
                (
                    "answer",
                    models.CharField(
                        choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")],
                        max_length=1,
                    ),
                ),
                ("difficulty_score", models.FloatField()),
                ("acceptance_score", models.FloatField()),
                ("is_accepted", models.BooleanField()),
                ("usage_score", models.IntegerField()),
                (
                    "reviewer",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviewer",
                        to="user.appuser",
                    ),
                ),
                (
                    "setter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="setter",
                        to="user.appuser",
                    ),
                ),
                (
                    "topic",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="question.topic"
                    ),
                ),
            ],
            options={
                "verbose_name": "Question",
                "verbose_name_plural": "Questions",
            },
        ),
    ]
