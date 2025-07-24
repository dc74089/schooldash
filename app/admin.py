from django.contrib import admin

from app.models import ScheduleOverride, AiSummaryLog

# Register your models here.
admin.site.register(ScheduleOverride)
admin.site.register(AiSummaryLog)