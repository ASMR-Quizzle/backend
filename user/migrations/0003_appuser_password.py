# Generated by Django 4.1 on 2022-08-17 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0002_alter_appuser_is_reviewer_alter_appuser_is_setter"),
    ]

    operations = [
        migrations.AddField(
            model_name="appuser",
            name="password",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
