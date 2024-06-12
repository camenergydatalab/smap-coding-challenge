from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.summary),
    re_path(r'^summary/', views.summary),
    re_path(r'^detail/', views.detail),
]
