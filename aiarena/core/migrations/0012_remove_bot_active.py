# Generated by Django 3.0.8 on 2020-12-27 23:39

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0011_auto_20201225_0629"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="bot",
            name="active",
        ),
    ]
