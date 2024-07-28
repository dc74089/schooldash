from datetime import timedelta

import requests
from django.utils import timezone


def helper_build_menu(day):
    try:
        out = {}
        station = "Other"

        for item in day['menu_items']:
            if item.get("is_section_title"):
                station = item.get("text")

                if not station:
                    station = item.get("image_alt")

                if not station:
                    station = "Other"

                if station not in out:
                    out[station] = []
            elif item.get("food"):
                food = item['food']

                if food.get("name"):
                    out[station].append(food['name'])

        return {key: value for key, value in out.items() if value}
    except:
        return {}


def lunch_menu():
    try:
        date = timezone.now().astimezone(timezone.get_default_timezone()).date()

        resp = requests.get(
            f"https://lhps.api.flikisdining.com/menu/api/weeks/school/charles-clayton-middle-school-campus-dining-hall/menu-type/lhp-us-lunch-available-daily-sides-651807093912170/{str(date.year)}/{str(date.month).zfill(2)}/{str(date.day).zfill(2)}/"
        ).json()

        menu_today = {}

        for day in resp['days']:
            if date.strftime("%Y-%m-%d") == day['date']:
                menu_today = helper_build_menu(day)

        return menu_today

    except:
        return None