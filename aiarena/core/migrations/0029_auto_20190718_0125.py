# Generated by Django 2.1.7 on 2019-07-17 15:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_participant_match_log'),
    ]

    operations = [
        migrations.RenameField(
            model_name='result',
            old_name='duration',
            new_name='game_steps',
        ),
    ]
