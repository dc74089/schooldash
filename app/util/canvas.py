import re

import requests
from dateutil.parser import parser


def get_name(request, course_id):
    return dict(request.session['names']).get(course_id, "Unknown Course")


def get_activity_stream(request):
    resp = requests.get("https://lhps.instructure.com/api/v1/users/self/activity_stream", headers={
        "Authorization": f"Bearer {request.session['access_token']}"
    })

    resp = resp.json()

    for activity in resp:
        print(activity['message'])
        activity['message'] = re.sub("<script.*/script>", '', activity['message'])
        activity['message'] = re.sub("<link [^>]*>(.*</link>)?", '', activity['message'])

    return resp


def get_todo(request):
    resp = requests.get("https://lhps.instructure.com/api/v1/users/self/todo", headers={
        "Authorization": f"Bearer {request.session['access_token']}"
    })

    resp = resp.json()

    for item in resp:
        item['assignment']['due_at'] = parser.parse(item['assignment']['due_at']).date()
        item['course'] = get_name(request, item['course_id'])

    return resp



def get_grades_and_set_names(request):
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
