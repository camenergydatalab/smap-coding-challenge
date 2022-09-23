from django.urls import path
from . import views

urlpatterns = [
    path(r'^$', views.summary),
    path(r'^summary/', views.summary),
    path(r'^detail/', views.detail),
]
