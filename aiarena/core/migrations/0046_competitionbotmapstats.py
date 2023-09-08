# Generated by Django 3.2.9 on 2022-03-09 11:48

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import aiarena.core.validators


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0045_auto_20220222_2343"),
    ]

    operations = [
        migrations.CreateModel(
            name="CompetitionBotMapStats",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("match_count", models.IntegerField(blank=True, null=True)),
                ("win_count", models.IntegerField(blank=True, null=True)),
                (
                    "win_perc",
                    models.FloatField(
                        blank=True,
                        null=True,
                        validators=[aiarena.core.validators.validate_not_nan, aiarena.core.validators.validate_not_inf],
                    ),
                ),
                ("loss_count", models.IntegerField(blank=True, null=True)),
                (
                    "loss_perc",
                    models.FloatField(
                        blank=True,
                        null=True,
                        validators=[aiarena.core.validators.validate_not_nan, aiarena.core.validators.validate_not_inf],
                    ),
                ),
                ("tie_count", models.IntegerField(blank=True, null=True)),
                (
                    "tie_perc",
                    models.FloatField(
                        blank=True,
                        null=True,
                        validators=[aiarena.core.validators.validate_not_nan, aiarena.core.validators.validate_not_inf],
                    ),
                ),
                ("crash_count", models.IntegerField(blank=True, null=True)),
                (
                    "crash_perc",
                    models.FloatField(
                        blank=True,
                        null=True,
                        validators=[aiarena.core.validators.validate_not_nan, aiarena.core.validators.validate_not_inf],
                    ),
                ),
                ("updated", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "bot",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="competition_map_stats",
                        to="core.competitionparticipation",
                    ),
                ),
                ("map", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.map")),
            ],
        ),
    ]
