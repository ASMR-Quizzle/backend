# Generated by Django 4.1 on 2022-08-18 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("question", "0004_remove_question_reviewer_question_reviewer"),
    ]

    operations = [
        migrations.RenameField(
            model_name="question",
            old_name="reviewer",
            new_name="reviewers",
        ),
        migrations.AddField(
            model_name="question",
            name="reviews",
            field=models.IntegerField(default=0),
        ),
    ]
