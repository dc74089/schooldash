from django.urls import path

from app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('canvas/oauth', views.oauth, name='canvas_oauth'),
]