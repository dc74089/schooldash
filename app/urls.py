from django.urls import path

from app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('lunch', views.lunch, name='lunch'),
    path('noitf', views.notif, name='notif'),
    path('todo', views.todo, name='todo'),
    path('grades', views.grades, name='grades'),

    path('config', views.config, name='config'),
    path('reset', views.reset, name='reset'),

    path('canvas/oauth', views.oauth, name='canvas_oauth'),
]