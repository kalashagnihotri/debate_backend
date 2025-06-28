# Generated manually to add missing reply_to field

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("debates", "0013_add_missing_columns"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="reply_to",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="replies",
                to="debates.message",
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="is_flagged",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="message",
            name="flagged_reason",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="message",
            name="is_hidden",
            field=models.BooleanField(default=False),
        ),
    ]
