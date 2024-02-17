from django.urls import path
from . import views

urlpatterns = [
    path("", views.summary, name="summary"),
    path("summary/", views.summary, name="summary"),
    path("detail/", views.detail, name="detail"),
]
