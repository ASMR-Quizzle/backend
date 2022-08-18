# Generated by Django 4.1 on 2022-08-18 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0004_appuser_phone_number"),
        ("question", "0006_question_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="reviewers",
            field=models.ManyToManyField(
                blank=True, related_name="reviewer", to="user.appuser"
            ),
        ),
    ]