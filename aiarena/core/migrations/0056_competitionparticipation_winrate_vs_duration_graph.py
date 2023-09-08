# Generated by Django 3.2.15 on 2022-11-07 11:01

from django.db import migrations, models

import aiarena.core.models.competition_participation
import aiarena.core.storage


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0055_match_first_started"),
    ]

    operations = [
        migrations.AddField(
            model_name="competitionparticipation",
            name="winrate_vs_duration_graph",
            field=models.FileField(
                blank=True,
                null=True,
                storage=aiarena.core.storage.OverwriteStorage(),
                upload_to=aiarena.core.models.competition_participation.winrate_vs_duration_graph_upload_to,
            ),
        ),
    ]
