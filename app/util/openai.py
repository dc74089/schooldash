import json
import os
from datetime import datetime, time, date, timedelta
from pprint import pprint

from django.http import HttpResponseBase
from django.utils import timezone

from app.util import lunch, canvas
from app.util.bells import get_schedule_name, get_bell_schedule

EXPIRY = timedelta(minutes=30)

DEV_PROMPT = """
You are a friendly and smart assistant for a middle school student dashboard. Using the context provided—such as the current time and date, schedule type, grade level, upcoming assignments, missing assignments, and meal menus—generate a brief and helpful summary of the student's day.

Your response must follow these rules:

* Format the output as **exactly three concise Markdown bullet points** (using `*`). Each should focus on what's most useful or relevant right now.
* **Only mention breakfast if it's early in the day** and **only mention lunch if it's still ahead**—don't include meals that have likely already happened.
* **Avoid long lists.** For meals or assignments, mention just the highlights.
* If there’s a **group of assignments due soon**, briefly point that out and offer a quick, supportive time management tip.
* If the bell_schedule is present, use it to help reference the school day. If it's missing, do not assume school is canceled—just avoid mentioning specific class times or blocks.
* If the `canvas-todo-list` or `canvas-missing-assignments` is empty or missing, do *not* assume the student has no assignments—just don’t reference it directly.
* Use friendly names for schedule blocks. For instance, "Prime Time" instead of "PT", or "2nd Period" instead of "2".
* Give information that will continue to be relevant for at least half an hour, as this dashboard does not refresh frequently.

You need to know the following to interpret the bell schedule:
* The schedule is a tuple of tuples. Each inner tuple is the name of the period, the start time, and the end time.
* PT stands for **Prime Time**, which is an optional time before and after every school day where students can visit teachers to ask questions or make-up assignments. They need an appointment with the teacher to take advantage of this time (make sure to include that fact if you encourage students to take advantage of prime time).
* **Advisory** is our school's version of homeroom. 
* Disco stands for **Discovery Groups**. During this time, students are assigned a different teacher each week, and they learn non-curricular lessons aligning with a personal passion of the teacher's.
* Study stands for **Directed Study**, which is our school's version of study hall. Students report to their advisory teacher's classroom for this.

Keep the tone friendly, clear, and supportive. Speak directly to the student in plain language with proper grammar. Your goal is to help them feel prepared, not overwhelmed.

The context will follow this message.

"""


def get_client():
    from openai import OpenAI
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))


def datetime_handler(obj):
    if isinstance(obj, (datetime, time, date)):
        return obj.isoformat()
    if isinstance(obj, HttpResponseBase):
        return []
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def get_todo_summary(request):
    sesh = request.session
    if 'todo_summary' in sesh and datetime.now().timestamp() - sesh['todo_summary_time'] < EXPIRY.total_seconds():
        return sesh['todo_summary']
    
    context = {}

    grade = int(request.session.get('grade', -1000))

    context['grade'] = grade
    context['current-time'] = datetime.now().astimezone(timezone.get_default_timezone()).strftime("%I:%M %p")
    context['current-date'] = datetime.now().astimezone(timezone.get_default_timezone()).strftime("%A %Y-%m-%d")

    if datetime.now().astimezone(timezone.get_default_timezone()).time() < time(15):  # It's still during the day so schedule is relevant
        context['bell-schedule-name'] = get_schedule_name()
        context['bell-schedule-data'] = get_bell_schedule(grade)

    if datetime.now().astimezone(timezone.get_default_timezone()).time() < time(10):
        context['fling-menu'] = lunch.fling_menu()

    if datetime.now().astimezone(timezone.get_default_timezone()).time() < time(12, 30):
        context['lunch-menu'] = lunch.lunch_menu()

    if 'access_token' in request.session:  # Canvas is (probably) authed
        try:
            context['canvas-todo-list'] = canvas.get_todo(request)
            context['canvas-missing-assignments'] = canvas.get_missing(request)
        except:
            pass

    context_string = json.dumps(context, default=datetime_handler)

    client = get_client()

    resp = client.responses.create(
        model="o4-mini",
        input=[
            {
                "role": "developer",
                "content": DEV_PROMPT
            },
            {
                "role": "user",
                "content": context_string,
            }
        ]
    )
    
    sesh['todo_summary'] = resp.output_text
    sesh['todo_summary_time'] = datetime.now().timestamp()

    return resp.output_text
