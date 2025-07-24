from django.contrib import admin

from app.models import ScheduleOverride, AiSummaryLog, FeatureFlag

# Register your models here.
admin.site.register(ScheduleOverride)
admin.site.register(AiSummaryLog)
admin.site.register(FeatureFlag)