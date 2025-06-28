# Generated manually to add created_by field to DebateTopic

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('debates', '0010_add_vote_model'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='debatetopic',
            name='created_by',
            field=models.ForeignKey(
                blank=True,
                help_text='The moderator who created this topic',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='created_topics',
                to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
