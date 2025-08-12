import json
import os
from datetime import datetime, time, date, timedelta
from pprint import pprint

from dateutil.parser import parse
from django.conf import settings
from django.http import HttpResponseBase
from django.utils import timezone
from pydantic import BaseModel

from app.models import AiSummaryLog
from app.util import lunch, canvas
from app.util.bells import get_schedule_name, get_bell_schedule


class AgentResponse(BaseModel):
    output_text: str
    expires_at: str


EXPIRY = timedelta(minutes=30)

DEV_PROMPT = """
You are a friendly, smart assistant writing a short summary message for a middle school student dashboard. Use the provided context (such as current time and date, schedule type, grade level, upcoming assignments, missing assignments, meal menus, and bell schedule) to generate a brief, supportive summary of what’s most relevant to the student right now.

**Format and rules:**

* Your response must be **exactly three concise Markdown bullet points** (using `*`), each highlighting timely, useful information.
* Include an `expires_at` field with each response—use an POSIX timestamp that reflects when the message will no longer be valid (e.g. the end of the current class period).
* Do not include the `expires_at` field in the `output_text`.
* Mention **breakfast only early in the day**, and **lunch only if it's still upcoming**. Skip meals that have likely already happened.
* Avoid long lists—only highlight key items (e.g. one or two assignments or meal items).
* If several assignments are due soon, say so and include a brief, encouraging time management tip.
* If a `bell_schedule` is present, use it to reference specific periods. If it’s missing, don’t assume school is canceled—just avoid naming times or blocks.
* If `canvas-todo-list` or `canvas-missing-assignments` is empty or missing, don’t say the student has no work—just don’t reference those lists.
* Use friendly names for blocks (e.g. “2nd Period” instead of “2”, “Prime Time” instead of “PT”).
* Give information that will remain relevant for **at least 30 minutes**, since the dashboard refreshes infrequently.

**Bell schedule terms you should understand:**

* Each entry in the bell schedule is a tuple: `(period_name, start_time, end_time)`.
* “PT” = **Prime Time** – optional time before/after school for meeting with teachers (by appointment only).
* “Advisory” = our version of **homeroom**.
* “Disco” = **Discovery Groups** – a non-curricular class based on the teacher’s interests.
* “Study” = **Directed Study** – our school’s version of study hall (held in advisory rooms).

Keep the tone warm, clear, and encouraging. Speak directly to the student in plain language with correct grammar. Your goal is to help them feel calm, confident, and ready for the day.

The context will follow this prompt.

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

    print(
        datetime.now().astimezone(timezone.get_default_timezone()).timestamp(),
        float(sesh.get('todo_summary_expires_at', 0)),
        datetime.now().astimezone(timezone.get_default_timezone()).timestamp() < float(sesh.get('todo_summary_expires_at', 0))
    )

    if not settings.DEBUG and 'todo_summary' in sesh and 'todo_summary_expires_at' in sesh \
            and datetime.now().astimezone(timezone.get_default_timezone()).timestamp() < float(sesh['todo_summary_expires_at']):
        return sesh['todo_summary']

    context = {}

    grade = int(request.session.get('grade', -1000))

    context['grade'] = grade
    context['current-time'] = datetime.now().astimezone(timezone.get_default_timezone()).strftime("%I:%M %p")
    context['current-time-posix'] = datetime.now().astimezone(timezone.get_default_timezone()).timestamp()
    context['current-date'] = datetime.now().astimezone(timezone.get_default_timezone()).strftime("%A %Y-%m-%d")

    if datetime.now().astimezone(timezone.get_default_timezone()).time() < time(
            15):  # It's still during the day so schedule is relevant
        context['bell-schedule-name'] = get_schedule_name(grade)
        context['bell-schedule-data'] = get_bell_schedule(grade)

    if datetime.now().astimezone(timezone.get_default_timezone()).time() < time(10):
        context['fling-menu'] = lunch.fling_menu(grade)

    if datetime.now().astimezone(timezone.get_default_timezone()).time() < time(12, 30):
        context['lunch-menu'] = lunch.lunch_menu(grade)

    if 'access_token' in request.session:  # Canvas is (probably) authed
        try:
            context['canvas-todo-list'] = canvas.get_todo(request)
            context['canvas-missing-assignments'] = canvas.get_missing(request)
        except:
            pass

    context_string = json.dumps(context, default=datetime_handler)

    client = get_client()

    resp = client.responses.parse(
        model=settings.OPENAI_MODEL,
        input=[
            {
                "role": "developer",
                "content": DEV_PROMPT
            },
            {
                "role": "user",
                "content": context_string,
            }
        ],
        text_format=AgentResponse
    )

    sesh['todo_summary'] = resp.output_parsed.output_text
    sesh['todo_summary_expires_at'] = min(float(resp.output_parsed.expires_at), datetime.now().astimezone(timezone.get_default_timezone()).timestamp() + EXPIRY.total_seconds())
    sesh['todo_summary_time'] = datetime.now().astimezone(timezone.get_default_timezone()).timestamp()

    log = AiSummaryLog(
        summary=resp.output_parsed.output_text,
        expires=datetime.fromtimestamp(float(resp.output_parsed.expires_at), timezone.get_default_timezone()),
        generated=datetime.now().astimezone(timezone.get_default_timezone()),
        context=context_string,
        person_id=request.session.get('canvas_uid', -1)
    )

    log.save()

    return resp.output_parsed.output_text
