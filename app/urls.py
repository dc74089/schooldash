from django.urls import path

from app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('fling', views.fling, name='fling'),
    path('lunch', views.lunch, name='lunch'),
    path('noitf', views.notif, name='notif'),
    path('todo', views.todo, name='todo'),
    path('missing', views.missing, name='missing'),
    path('grades', views.grades, name='grades'),
    path('ai', views.ai_summary, name='ai_summary'),

    path('config', views.config, name='config'),
    path('reset', views.reset, name='reset'),

    path('dev/sy', views.dashboard, name='reset'),
    path('dev/summer', views.summer, name='reset'),

    path('canvas/oauth', views.oauth, name='canvas_oauth'),
    path('favicon.svg', views.favicon, name='favicon'),
]