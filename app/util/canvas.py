import os
import re
from datetime import timedelta

import requests
from dateutil.parser import parse
from django.http.response import HttpResponseForbidden
from django.utils import timezone


def get_name(request, course_id):
    return dict(request.session['names']).get(course_id, "Unknown Course")


def do_refresh_if_needed(request):
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


def get_activity_stream(request):
    try:
        do_refresh_if_needed(request)

        resp = requests.get("https://lhps.instructure.com/api/v1/users/self/activity_stream", headers={
            "Authorization": f"Bearer {request.session['access_token']}"
        })

        resp = resp.json()

        for activity in resp:
            activity['message'] = re.sub("<script.*/script>", '', activity['message'])
            activity['message'] = re.sub("<link [^>]*>(.*</link>)?", '', activity['message'])

        return resp
    except TypeError:
        del request.session['access_token']
        del request.session['refresh_token']

        request.session.save()

        return HttpResponseForbidden()


def get_todo(request):
    try:
        do_refresh_if_needed(request)

        resp = requests.get("https://lhps.instructure.com/api/v1/users/self/todo", headers={
            "Authorization": f"Bearer {request.session['access_token']}"
        })

        resp = resp.json()

        for item in resp:
            item['assignment']['due_at'] = parse(item['assignment']['due_at']).date()
            item['course'] = get_name(request, item['course_id'])

        return resp
    except TypeError:
        del request.session['access_token']
        del request.session['refresh_token']

        request.session.save()

        return HttpResponseForbidden()


def get_grades_and_set_names(request):
    try:
        do_refresh_if_needed(request)

        resp = requests.get("https://lhps.instructure.com/api/v1/courses", headers={
            "Authorization": f"Bearer {request.session['access_token']}"
        }, params={
            "enrollment_type": "student",
            "enrollment_state": "active",
            "include[]": ["total_scores", "current_grading_period_scores"],
            "per_page": 100,
        })

        resp = resp.json()

        request.session['names'] = {item['id']: item['name'] for item in resp}
        request.session.save()

        return resp
    except TypeError:
        del request.session['access_token']
        del request.session['refresh_token']

        request.session.save()

        return HttpResponseForbidden()
