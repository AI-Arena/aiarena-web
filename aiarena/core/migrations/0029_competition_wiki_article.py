# Generated by Django 3.0.14 on 2021-07-12 05:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0003_mptt_upgrade'),
        ('core', '0028_auto_20210419_2336'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='wiki_article',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='wiki.Article'),
        ),
    ]
