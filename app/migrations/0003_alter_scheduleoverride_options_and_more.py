# Generated by Django 4.2.13 on 2024-11-06 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_canvastoken'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='scheduleoverride',
            options={'ordering': ['-date']},
        ),
        migrations.AddField(
            model_name='scheduleoverride',
            name='schedule_link',
            field=models.TextField(blank=True, null=True),
        ),
    ]