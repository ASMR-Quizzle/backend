# Generated by Django 4.1 on 2022-08-25 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("question", "0013_csvfile"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="reviewer_notes",
            field=models.TextField(default=""),
        ),
    ]