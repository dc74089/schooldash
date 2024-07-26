from dateutil.parser import parse
from django.utils import timezone

from app.models import ScheduleOverride


def transform(arr):
    return tuple(
        ((x[0], parse(x[1]).time(), parse(x[2]).time()) for x in arr)
    )


normal_7 = transform((
    ("PT", "7:30", "8:00"),
    ("1", "8:10", "8:55"),
    ("Fling", "8:55", "9:10"),
    ("2", "9:15", "10:00"),
    ("3", "10:05", "10:50"),
    ("4", "10:55", "11:40"),
    ("Lunch", "11:40", "12:20"),
    ("5", "12:25", "13:10"),
    ("6", "13:15", "14:00"),
    ("7", "14:05", "14:50"),
    ("PT", "14:50", "15:30"),
))

normal_8 = transform((
    ("PT", "7:30", "8:00"),
    ("1", "8:10", "8:55"),
    ("Fling", "8:55", "9:10"),
    ("2", "9:15", "10:00"),
    ("3", "10:05", "10:50"),
    ("4", "10:55", "11:40"),
    ("5", "11:45", "12:30"),
    ("Lunch", "12:30", "13:10"),
    ("6", "13:15", "14:00"),
    ("7", "14:05", "14:50"),
    ("PT", "14:50", "15:30"),
))

wed_7 = transform((
    ("PT", "7:30", "8:00"),
    ("2", "8:10", "9:25"),
    ("Unity", "9:30", "9:55"),
    ("Fling", "9:55", "10:10"),
    ("4", "10:15", "11:30"),
    ("Advisory", "11:35", "12:10"),
    ("Lunch", "12:10", "12:40"),
    ("6", "12:45", "14:00"),
    ("Study", "14:05", "14:50"),
    ("PT", "14:50", "15:30"),
))

wed_8 = transform((
    ("PT", "7:30", "8:00"),
    ("2", "8:10", "9:25"),
    ("Unity", "9:30", "9:55"),
    ("Fling", "9:55", "10:10"),
    ("4", "10:15", "11:30"),
    ("Lunch", "11:30", "12:00"),
    ("Advisory", "12:05", "12:40"),
    ("6", "12:45", "14:00"),
    ("Study", "14:05", "14:50"),
    ("PT", "14:50", "15:30"),
))

thurs_7 = transform((
    ("PT", "7:30", "8:00"),
    ("1", "8:10", "9:25"),
    ("Fling", "9:25", "9:40"),
    ("3", "9:45", "11:00"),
    ("Disco", "11:05", "11:40"),
    ("Lunch", "11:40", "12:10"),
    ("5", "12:15", "13:30"),
    ("7", "13:35", "14:50"),
    ("PT", "14:50", "15:30"),
))

thurs_8 = transform((
    ("PT", "7:30", "8:00"),
    ("1", "8:10", "9:25"),
    ("Fling", "9:25", "9:40"),
    ("3", "9:45", "11:00"),
    ("Lunch", "11:05", "11:30"),
    ("Disco", "11:35", "12:10"),
    ("5", "12:15", "13:30"),
    ("7", "13:35", "14:50"),
    ("PT", "14:50", "15:30"),
))

early = transform((
    ("PT", "7:30", "8:00"),
    ("1", "8:10", "8:40"),
    ("Fling", "8:40", "8:55"),
    ("2", "9:00", "9:30"),
    ("3", "9:35", "10:05"),
    ("4", "10:10", "10:40"),
    ("5", "10:45", "11:15"),
    ("6", "11:20", "11:50"),
    ("7", "11:55", "12:25"),
))

amass_7 = transform((
    ("PT", "7:30", "8:00"),
    ("2", "8:10", "9:25"),
    ("Fling", "9:25", "9:45"),
    ("Assembly", "9:50", "10:55"),
    ("Advisory", "10:55", "11:35"),
    ("Lunch", "11:35", "12:10"),
    ("4", "12:15", "13:30"),
    ("6", "13:35", "14:50"),
    ("PT", "14:50", "15:30"),
))

amass_8 = transform((
    ("PT", "7:30", "8:00"),
    ("2", "8:10", "9:25"),
    ("Fling", "9:25", "9:45"),
    ("Assembly", "9:50", "10:55"),
    ("Lunch", "10:50", "11:25"),
    ("Advisory", "11:30", "12:10"),
    ("4", "12:15", "13:30"),
    ("6", "13:35", "14:50"),
    ("PT", "14:50", "15:30"),
))

pmass_7 = transform((
    ("PT", "7:30", "8:00"),
    ("2", "8:10", "9:25"),
    ("Fling", "9:25", "9:45"),
    ("4", "9:50", "11:05"),
    ("Advisory", "11:10", "11:50"),
    ("Lunch", "11:50", "12:25"),
    ("6", "12:30", "13:45"),
    ("Assembly", "13:50", "14:50"),
    ("PT", "14:50", "15:30"),
))

pmass_8 = transform((
    ("PT", "7:30", "8:00"),
    ("2", "8:10", "9:25"),
    ("Fling", "9:25", "9:45"),
    ("4", "9:50", "11:05"),
    ("Lunch", "11:05", "11:40"),
    ("Advisory", "11:45", "12:25"),
    ("6", "12:30", "13:45"),
    ("Assembly", "13:50", "14:50"),
    ("PT", "14:50", "15:30"),
))


def get_bell_schedule(grade):
    soq = ScheduleOverride.objects.filter(date=timezone.now().date())

    if soq.exists():
        override: ScheduleOverride = soq.first()

        if override.schedule == "all":
            return normal_8 if grade == 8 else normal_7
        elif override.schedule == "wed":
            return wed_8 if grade == 8 else wed_7
        elif override.schedule == "thurs":
            return thurs_8 if grade == 8 else thurs_7
        elif override.schedule == "early":
            return early
        elif override.schedule == "amass":
            return amass_8 if grade == 8 else amass_7
        elif override.schedule == "pmass":
            return pmass_8 if grade == 8 else pmass_7
        else:
            return None
    else:
        today = timezone.now().date()

        if today.weekday() in (0, 1, 4):
            return normal_8 if grade == 8 else normal_7
        elif today.weekday() == 2:
            return wed_8 if grade == 8 else wed_7
        elif today.weekday() == 3:
            return thurs_8 if grade == 8 else thurs_7
        else:
            return None
