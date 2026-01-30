from django.contrib import admin

from app.models import ScheduleOverride, AiSummaryLog, FeatureFlag, BetaUser, CountdownEvent

# Register your models here.
admin.site.register(ScheduleOverride)
admin.site.register(AiSummaryLog)
admin.site.register(FeatureFlag)
admin.site.register(BetaUser)
admin.site.register(CountdownEvent)