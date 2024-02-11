from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    url(r"^$", views.summary),
    url(r"^summary/", views.summary),
    path(r"detail/<int:user_id>/", views.detail),
]
