# Generated by Django 3.2.16 on 2023-02-19 06:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("patreon", "0005_patreonunlinkeddiscorduid"),
    ]

    operations = [
        migrations.AddField(
            model_name="patreonaccountbind",
            name="last_refresh_attempt_current_user_json",
            field=models.TextField(blank=True, null=True),
        ),
    ]
