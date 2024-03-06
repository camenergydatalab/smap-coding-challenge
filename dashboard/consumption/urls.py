from django.conf.urls import url
from django.urls import path

from . import views

app_name = "consumption"
urlpatterns = [
    url(r"^$", views.summary),
    url(r"^summary/", views.summary),
    path("detail/<str:user_id>/", views.detail, name="detail"),
]
