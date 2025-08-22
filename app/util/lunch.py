from datetime import timedelta

import requests
from django.utils import timezone

from schooldash import settings


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


def fling_menu(grade):
    if grade not in (7, 8):
        return None

    try:
        date = timezone.now().astimezone(timezone.get_default_timezone()).date()

        resp = requests.get(
            f"https://lhps.api.flikisdining.com/menu/api/weeks/school/charles-clayton-middle-school-campus-dining-hall/menu-type/breakfast/{str(date.year)}/{str(date.month).zfill(2)}/{str(date.day).zfill(2)}/"
        ).json()

        menu_today = {}

        for day in resp['days']:
            if date.strftime("%Y-%m-%d") == day['date']:
                menu_today = helper_build_menu(day)

        if not settings.MOCK or menu_today:
            return menu_today
        else:
            return mock_breakfast_menu()

    except:
        if settings.MOCK:
            return mock_breakfast_menu()
        else:
            return None


def lunch_menu(grade):
    try:
        date = timezone.now().astimezone(timezone.get_default_timezone()).date()

        if grade in (7, 8):
            resp = requests.get(
                f"https://lhps.flikisdining.com/menu/charles-clayton-middle-school-campus-dining-hall/lhp-us-lunch-available-daily-sides-651807093912170/{str(date.year)}/{str(date.month).zfill(2)}/{str(date.day).zfill(2)}/"
            ).json()
        else:
            resp = requests.get(
                f"https://lhps.api.flikisdining.com/menu/api/weeks/school/grades-9-12/menu-type/lhp-us-lunch-available-daily-sides-651807093912170/{str(date.year)}/{str(date.month).zfill(2)}/{str(date.day).zfill(2)}/"
            ).json()

        menu_today = {}

        for day in resp['days']:
            if date.strftime("%Y-%m-%d") == day['date']:
                menu_today = helper_build_menu(day)

        if not settings.MOCK or menu_today:
            return menu_today
        else:
            return mock_menu()

    except:
        if settings.MOCK:
            return mock_menu()
        else:
            return None
    
    
    


def mock_menu():
    return {
        "Main Dishes": [
            "Grilled Chicken Breast",
            "Spaghetti and Meatballs",
            "Vegetable Stir Fry"
        ],
        "Sides": [
            "Steamed Rice",
            "Roasted Vegetables",
            "Garden Salad",
            "Mashed Potatoes"
        ],
        "Dessert": [
            "Chocolate Brownie"
        ]
    }

def mock_breakfast_menu():
    return {
        "Hot Items": [
            "Scrambled Eggs",
            "French Toast",
            "Bacon Strips",
            "Hash Browns"
        ],
        "Cold Items": [
            "Assorted Cereals",
            "Fresh Fruit",
            "Yogurt Parfait"
        ],
        "Beverages": [
            "Orange Juice",
            "Apple Juice",
            "Milk"
        ]
    }
