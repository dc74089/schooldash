import json
import os
from datetime import datetime, time, date
from pprint import pprint

from app.util import lunch, canvas
from app.util.bells import get_schedule_name


DEV_PROMPT = """
You are a friendly and smart assistant for a middle school student dashboard. Using the context provided—such as the current time and date, schedule type, grade level, upcoming assignments, and meal menus—generate a brief and helpful summary of the student's day.

Your response must follow these rules:

* Format the output as **exactly three concise Markdown bullet points** (using `*`). Each should focus on what's most useful or relevant right now.
* **Only mention breakfast if it's early in the day** and **only mention lunch if it's still ahead**—don't include meals that have likely already happened.
* **Avoid long lists.** For meals or assignments, mention just the highlights.
* If there’s a **group of assignments due soon**, briefly point that out and offer a quick, supportive time management tip.
* If a **bell schedule** is present, assume it’s a school day. If not, assume it's a day off and tailor the tone accordingly.
* If the `canvas-todo-list` is missing, do *not* assume the student has no assignments—just don’t reference it directly.

Keep the tone friendly, clear, and supportive. Speak directly to the student in plain language. Your goal is to help them feel prepared, not overwhelmed.

"""


def get_client():
    from openai import OpenAI
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))


def datetime_handler(obj):
    if isinstance(obj, (datetime, time, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def get_todo_summary(request):
    context = {}

    context['bell-schedule-name'] = get_schedule_name()
    context['fling-menu'] = lunch.fling_menu()
    context['lunch-menu'] = lunch.lunch_menu()
    context['grade'] = int(request.session.get('grade', -1000))
    context['current-time'] = datetime.now().strftime("%I:%M %p")
    context['current-date'] = datetime.now().strftime("%A %Y-%m-%d")

    if 'access_token' in request.session:  # Canvas is (probably) authed
        try:
            context['canvas-todo-list'] = canvas.get_todo(request)
        except:
            pass

    pprint(context)

    context_string = json.dumps(context, default=datetime_handler)

    client = get_client()

    resp = client.responses.create(
        model="o4-mini",
        input=DEV_PROMPT + context_string
    )

    return resp.output_text


