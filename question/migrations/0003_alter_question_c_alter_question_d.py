# Generated by Django 4.1 on 2022-08-18 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("question", "0002_rename_test_score_usereligibilitytest_test_type_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="C",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="question",
            name="D",
            field=models.TextField(blank=True, null=True),
        ),
    ]
