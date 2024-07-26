from django.db import models

# Create your models here.
schedules = (
    ("all", "Normal MTF"),
    ("wed", "Normal Wednesday"),
    ("thurs", "Normal Thursday"),
    ("early", "Early Dismissal"),
    ("amass", "AM Assembly"),
    ("pmass", "PM Assembly"),
    ("special", "Other"),
)


class ScheduleOverride(models.Model):
    date = models.DateField()
    schedule = models.CharField(max_length=20, choices=schedules)
