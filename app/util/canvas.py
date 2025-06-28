import os
import re
from datetime import timedelta
from pprint import pprint

import requests
from dateutil.parser import parse
from django.http.response import HttpResponseForbidden
from django.utils import timezone


def init_course_names(request):
    do_refresh_if_needed(request)

    resp = requests.get("https://lhps.instructure.com/api/v1/courses", headers={
        "Authorization": f"Bearer {request.session['access_token']}"
    }, params={
        "per_page": 100,
    })

    resp = resp.json()

    request.session['names'] = {item['id']: item['name'] for item in resp if 'name' in item}
    request.session.save()

    # print(request.session['names'])


def get_name(request, course_id):
    try:
        course_id = str(course_id)
        return dict(request.session['names']).get(course_id, "Unknown Course")
    except KeyError:
        return "Unknown Course"


def do_refresh_if_needed(request):
    if 'expires' in request.session:
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
        out = []

        for activity in resp:
            try:
                if activity.get("read_state", False): continue
            except:
                continue

            if 'message' in activity and activity['message']:
                activity['message'] = re.sub("<script.*/script>", '', activity['message'])
                activity['message'] = re.sub("<link [^>]*>(.*</link>)?", '', activity['message'])

            if 'course_id' in activity and activity['course_id']:
                activity['course'] = get_name(request, activity['course_id'])

            out.append(activity)

        return out
    except TypeError:
        del request.session['access_token']
        del request.session['refresh_token']

        request.session.save()

        return HttpResponseForbidden()
    except:
        return None


def get_todo(request):
    try:
        do_refresh_if_needed(request)

        resp = requests.get("https://lhps.instructure.com/api/v1/users/self/todo", headers={
            "Authorization": f"Bearer {request.session['access_token']}"
        })

        resp = resp.json()

        # pprint(resp)

        for item in resp:
            if 'assignment' in item and'due_at' in item['assignment']:
                if item['assignment']['due_at']:
                    item['assignment']['due_at'] = parse(item['assignment']['due_at']).date()

            if 'course' in item:
                item['course'] = get_name(request, item['course_id'])

        return resp
    except TypeError:
        del request.session['access_token']
        del request.session['refresh_token']

        request.session.save()

        return HttpResponseForbidden()


def get_missing(request):
    try:
        do_refresh_if_needed(request)

        resp = requests.get("https://lhps.instructure.com/api/v1/users/self/missing_submissions?filter[]=submittable&include[]=course", headers={
            "Authorization": f"Bearer {request.session['access_token']}"
        })

        resp = resp.json()

        # pprint(resp)

        for item in resp:
            if 'due_at' in item:
                if item['due_at']:
                    item['due_at'] = parse(item['due_at']).date()

            if 'course' in item:
                item['course'] = get_name(request, item['course_id'])

        # pprint(resp)

        return resp

    except TypeError:
        del request.session['access_token']
        del request.session['refresh_token']

        request.session.save()

        return HttpResponseForbidden()


def get_grades(request):
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

        return resp
    except TypeError:
        del request.session['access_token']
        del request.session['refresh_token']

        request.session.save()

        return HttpResponseForbidden()
    except:
        return None
