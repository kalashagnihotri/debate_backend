# Generated by Django 4.2.23 on 2025-06-22 10:52

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="date_joined",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="profile",
            name="last_active",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
