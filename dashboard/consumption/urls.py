from django.conf.urls import url
from django.urls import path

from . import views

app_name = "consumption"

urlpatterns = [
    url(r"^$", views.summary, name="index"),
    url(r"^summary/", views.summary, name="summary"),
    path(r"detail/<int:user_id>/", views.detail, name="detail"),
]
