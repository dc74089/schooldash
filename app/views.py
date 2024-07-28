import os
import traceback
from datetime import timedelta

import canvasapi
import requests
from django.shortcuts import render, redirect
from django.utils import timezone

from app.util import canvas, color
from app.util.bells import get_bell_schedule
from app.util.lunch import lunch_menu


def index(request):
    try:
        grade = request.session.get('grade', 0)
        primary = request.session.get('primary', "#c3002f")
        secondary = request.session.get('secondary', "#212137")
        dark = color.is_dark(secondary)

        print("Dark" if dark else "Light")

        if 'access_token' in request.session:
            if timezone.now().timestamp() >= request.session['expires']:
                resp = requests.post("https://lhps.instructure.com/login/oauth2/token", {
                    "grant_type": "refresh_token",
                    "client_id": "75360000000000229",
                    "client_secret": os.getenv("CANVAS_CLIENT_SECRET"),
                    "redirect_uri": "http://localhost:8000/canvas/oauth",
                    "refresh_token": request.session['refresh_token']
                })

                resp = resp.json()

                request.session['access_token'] = resp['access_token']
                request.session['expires'] = (
                            timezone.now() + timedelta(seconds=int(resp['expires_in']) - 60)).timestamp()
                request.session.save()

            grades = canvas.get_grades_and_set_names(request)

            return render(request, "app/index.html", {
                "primary": primary,
                "secondary": secondary,
                "bw": "white" if dark else "black",
                "background": request.session.get("background", "particle"),
                "dark": dark,
                "lunch_menu": lunch_menu(),
                "bells": get_bell_schedule(grade),
                "weekend": timezone.now().weekday() in (5, 6),
                "canvas_authed": True,
                "notifications": canvas.get_activity_stream(request),
                "todo": canvas.get_todo(request),
                "grades": grades
            })
        else:
            return render(request, "app/index.html", {
                "primary": primary,
                "secondary": secondary,
                "bw": "white" if dark else "black",
                "background": request.session.get("background", "particle"),
                "dark": dark,
                "lunch_menu": lunch_menu(),
                "bells": get_bell_schedule(grade),
                "weekend": timezone.now().weekday() in (5, 6),
                "canvas_authed": False,
                "scopes": " ".join((
                    "url:GET|/api/v1/users/self/activity_stream",
                    "url:GET|/api/v1/users/self/todo",
                    "url:GET|/api/v1/users/self/upcoming_events",
                    "url:GET|/api/v1/users/:user_id/missing_submissions",
                    "url:GET|/api/v1/users/:id",
                    "url:GET|/api/v1/users/:user_id/enrollments",
                    "url:GET|/api/v1/announcements",
                    "url:GET|/api/v1/users/self/course_nicknames",
                    "url:GET|/api/v1/courses",
                ))
            })
    except:
        print(traceback.format_exc())
        request.session.clear()
        return redirect("index")


def config(request):
    if request.method == "POST":
        if 'primary' in request.POST:
            request.session['primary'] = request.POST['primary']

        if 'secondary' in request.POST:
            request.session['secondary'] = request.POST['secondary']

        if 'background' in request.POST:
            request.session['background'] = request.POST['background']

    return redirect('index')


def reset(request):
    request.session.clear()
    return redirect('index')


def oauth(request):
    if 'error' in request.GET:
        print(request.GET['error'])
        return redirect('index')
    elif 'code' in request.GET:
        resp = requests.post('https://lhps.instructure.com/login/oauth2/token', {
            "code": request.GET['code'],
            "grant_type": "authorization_code",
            "client_id": "75360000000000229",
            "client_secret": os.getenv("CANVAS_CLIENT_SECRET"),
            "redirect_uri": "http://localhost:8000/canvas/oauth"
        })

        resp = resp.json()

        request.session['access_token'] = resp['access_token']
        request.session['refresh_token'] = resp['refresh_token']
        request.session['expires'] = (timezone.now() + timedelta(seconds=int(resp['expires_in']) - 60)).timestamp()

        return redirect('index')
