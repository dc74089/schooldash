from django.db import migrations, models


def hs_to_us(apps, schema_editor):
    ScheduleOverride = apps.get_model('app', 'ScheduleOverride')
    ScheduleOverride.objects.filter(school='HS').update(school='US')


def us_to_hs(apps, schema_editor):
    ScheduleOverride = apps.get_model('app', 'ScheduleOverride')
    ScheduleOverride.objects.filter(school='US').update(school='HS')


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_alter_countdownevent_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduleoverride',
            name='school',
            field=models.CharField(choices=[('MS', 'Middle School'), ('US', 'Upper School')], default='MS', max_length=5),
        ),
        migrations.RunPython(hs_to_us, us_to_hs),
    ]
