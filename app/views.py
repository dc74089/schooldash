import os
import traceback
from datetime import timedelta

import canvasapi
import requests
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.utils import timezone

from app.models import CanvasToken
from app.util import canvas, color
from app.util.bells import get_bell_schedule
from app.util.lunch import lunch_menu


def index(request):
    try:
        grade = request.session.get('grade', 0)
        primary = request.session.get('primary', "#c3002f")
        secondary = request.session.get('secondary', "#212137")
        pri_dark = color.is_dark(primary)
        sec_dark = color.is_dark(secondary)


        if 'access_token' in request.session:
            if timezone.now().timestamp() >= request.session['expires']:
                resp = requests.post("https://lhps.instructure.com/login/oauth2/token", {
                    "grant_type": "refresh_token",
                    "client_id": "75360000000000229",
                    "client_secret": os.getenv("CANVAS_CLIENT_SECRET"),
                    "redirect_uri": "https://dash.canora.us/canvas/oauth",
                    "refresh_token": request.session['refresh_token']
                })

                resp = resp.json()

                request.session['access_token'] = resp['access_token']
                request.session['expires'] = (
                        timezone.now() + timedelta(seconds=int(resp['expires_in']) - 60)).timestamp()
                request.session.save()

            return render(request, "app/index.html", {
                "primary": primary,
                "secondary": secondary,
                "pri_bw": "white" if pri_dark else "black",
                "bw": "white" if sec_dark else "black",
                "background": request.session.get("background", "particle"),
                "pri_dark": pri_dark,
                "dark": sec_dark,
                "bells": get_bell_schedule(grade),
                "weekend": timezone.now().weekday() in (5, 6),
                "canvas_authed": True
            })
        else:
            return render(request, "app/index.html", {
                "primary": primary,
                "secondary": secondary,
                "pri_bw": "white" if pri_dark else "black",
                "bw": "white" if sec_dark else "black",
                "background": request.session.get("background", "particle"),
                "pri_dark": pri_dark,
                "dark": sec_dark,
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


def favicon(request):
    primary = request.GET.get('primary', "#c3002f")
    secondary = request.GET.get('secondary', "#212137")

    return render(request, "app/house.svg", {
        "primary": primary,
        "secondary": secondary,
    }, content_type="image/svg+xml")


def lunch(request):
    lunch = lunch_menu()

    if lunch:
        return render(request, "app/part_lunchmenu.html", {
            "lunch_menu": lunch
        })

    else:
        return HttpResponseNotFound()


def notif(request):
    return render(request, "app/part_notif.html", {
        "notifications": canvas.get_activity_stream(request)
    })


def todo(request):
    return render(request, "app/part_todo.html", {
        "todo": canvas.get_todo(request)
    })


def grades(request):
    return render(request, "app/part_grades.html", {
        "grades": canvas.get_grades_and_set_names(request)
    })


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
            "redirect_uri": "https://dash.canora.us/canvas/oauth"
        })

        resp = resp.json()

        request.session['access_token'] = resp['access_token']
        request.session['refresh_token'] = resp['refresh_token']
        request.session['expires'] = (timezone.now() + timedelta(seconds=int(resp['expires_in']) - 60)).timestamp()

        request.session.save()

        userinfo_resp = requests.get(
            "https://lhps.instructure.com/api/v1/users/self",
            headers={"Authorization": f"Bearer {request.session['access_token']}"}
        )

        userinfo_resp = userinfo_resp.json()

        ct = CanvasToken(
            token=resp['access_token'],
            refresh_token=resp['refresh_token'],
            person_id=userinfo_resp['id']
        )

        ct.save()
        ct.prune_other_tokens()

        return redirect('index')
