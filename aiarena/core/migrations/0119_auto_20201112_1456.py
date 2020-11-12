# Generated by Django 3.0.8 on 2020-11-12 12:56

import aiarena.core.models.season
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0118_auto_20201103_2121'),
    ]

    operations = [
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('type', models.CharField(choices=[('T', 'Tournament'), ('L', 'League'), ('C', 'Custom'), ('F', 'FlashChallenge')], default='L', max_length=32)),
                ('enabled', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='season',
            name='replay_archive_zip',
            field=models.FileField(blank=True, null=True, upload_to=aiarena.core.models.season.replay_archive_upload_to),
        ),
        migrations.CreateModel(
            name='Division',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='divisions', to='core.Competition')),
            ],
        ),
        migrations.AddField(
            model_name='bot',
            name='divisions',
            field=models.ManyToManyField(related_name='bots', to='core.Division'),
        ),
        migrations.AddField(
            model_name='map',
            name='competition',
            field=models.ManyToManyField(to='core.Competition'),
        ),
        migrations.AddField(
            model_name='season',
            name='competition',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.Competition'),
            preserve_default=False,
        ),
    ]
