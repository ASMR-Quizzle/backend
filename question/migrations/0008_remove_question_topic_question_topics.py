# Generated by Django 4.1 on 2022-08-18 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("question", "0007_alter_question_reviewers"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="question",
            name="topic",
        ),
        migrations.AddField(
            model_name="question",
            name="topics",
            field=models.ManyToManyField(to="question.topic"),
        ),
    ]
