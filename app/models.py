import os

import requests
from django.db import models
from django.utils import timezone

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


class FeatureFlag(models.Model):
    name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=False)

    def __bool__(self):
        return self.enabled

    def __str__(self):
        return self.name


class BetaUser(models.Model):
    canvas_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ScheduleOverride(models.Model):
    date = models.DateField()
    schedule = models.CharField(max_length=20, choices=schedules)
    schedule_link = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.date}: {self.get_schedule_display()}"


class CanvasToken(models.Model):
    token = models.CharField(max_length=100)
    refresh_token = models.CharField(max_length=100)
    person_id = models.CharField(max_length=100)

    def refresh_and_delete(self):
        try:
            resp = requests.post("https://lhps.instructure.com/login/oauth2/token", {
                "grant_type": "refresh_token",
                "client_id": "75360000000000229",
                "client_secret": os.getenv("CANVAS_CLIENT_SECRET"),
                "redirect_uri": "https://dash.canora.us/canvas/oauth",
                "refresh_token": self.refresh_token
            })

            resp = resp.json()
            print(resp)

            requests.delete(
                'https://lhps.instructure.com/login/oauth2/token',
                headers={"Authorization": f"Bearer {resp['access_token']}"}
            )

        except KeyError:
            pass  # Token has already been deleted

        self.delete()

    def prune_other_tokens(self):
        tq = CanvasToken.objects.filter(person_id=self.person_id).exclude(token=self.token)

        if tq.count() > 2:
            for tok in tq:
                tok.refresh_and_delete()


class AiSummaryLog(models.Model):
    summary = models.TextField()
    generated = models.DateTimeField()
    expires = models.DateTimeField()
    person_id = models.CharField(max_length=100)
    context = models.TextField()

    def __str__(self):
        return f"{self.person_id} - {self.generated.astimezone(timezone.get_default_timezone())}"
