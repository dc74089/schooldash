import os

import requests
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


class CanvasToken(models.Model):
    token = models.CharField(max_length=100)
    refresh_token = models.CharField(max_length=100)
    person_id = models.CharField(max_length=100)

    def refresh_and_delete(self):
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

        self.delete()

    def prune_other_tokens(self):
        tq = CanvasToken.objects.filter(person_id=self.person_id).exclude(token=self.token)

        for tok in tq:
            tok.refresh_and_delete()
