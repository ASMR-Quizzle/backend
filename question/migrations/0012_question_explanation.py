# Generated by Django 4.1 on 2022-08-21 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("question", "0011_usereligibilitytesttracker_duration"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="explanation",
            field=models.CharField(default="N/A", max_length=10000),
        ),
    ]