from django.conf.urls import url
from django.urls import path

from . import views

app_name = "consumption"
urlpatterns = [
    url(r"^$", views.summary),
    path("summary/", views.summary, name="summary"),
    path("detail/<str:user_id>/", views.detail, name="detail"),
]
