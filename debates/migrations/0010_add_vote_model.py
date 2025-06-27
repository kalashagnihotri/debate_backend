# Custom migration to add Vote model
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('debates', '0009_alter_debatevote_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('vote_type', models.CharField(
                    choices=[('BEST_ARGUMENT', 'Best Argument'), ('WINNING_SIDE', 'Winning Side')], 
                    help_text='Type of vote: BEST_ARGUMENT or WINNING_SIDE', 
                    max_length=20
                )),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('debate_session', models.ForeignKey(
                    help_text='The debate session this vote belongs to',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='votes',
                    to='debates.debatesession'
                )),
                ('user', models.ForeignKey(
                    help_text='The user who cast this vote (must be a student)',
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Vote',
                'verbose_name_plural': 'Votes',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='vote',
            index=models.Index(fields=['debate_session', 'vote_type'], name='debates_vot_debate__3abf98_idx'),
        ),
        migrations.AddIndex(
            model_name='vote',
            index=models.Index(fields=['user', '-created_at'], name='debates_vot_user_id_876bfb_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together={('user', 'debate_session')},
        ),
    ]
