# Generated by Django 3.0.8 on 2020-10-12 00:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0116_user_sync_patreon_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='supported_expiration_date',
            field=models.DateField(blank=True, default=None, null=True),
        ),
    ]