# Generated by Django 3.0.8 on 2021-01-06 06:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0013_map_game_mode"),
    ]

    operations = [
        migrations.AlterField(
            model_name="competition",
            name="name",
            field=models.CharField(default="Unknown", max_length=50, unique=True),
            preserve_default=False,
        ),
    ]
