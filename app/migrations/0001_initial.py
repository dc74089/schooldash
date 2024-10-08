# Generated by Django 4.2.13 on 2024-07-26 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduleOverride',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('schedule', models.CharField(choices=[('all', 'Normal MTF'), ('wed', 'Normal Wednesday'), ('thurs', 'Normal Thursday'), ('early', 'Early Dismissal'), ('amass', 'AM Assembly'), ('pmass', 'PM Assembly'), ('special', 'Other')], max_length=20)),
            ],
        ),
    ]
