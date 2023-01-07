from django.urls import path

from . import views

app_name = "consumption"

urlpatterns = [
    path("", views.SummaryView.as_view()),
    path("summary/", views.SummaryView.as_view(), name="summary"),
    path("detail/<int:user_id>/", views.UserDetailView.as_view(), name="detail"),
]
