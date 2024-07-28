from django.urls import path

from app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('config', views.config, name='config'),
    path('reset', views.reset, name='reset'),
    path('canvas/oauth', views.oauth, name='canvas_oauth'),
]