from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"^$", views.SummaryView.as_view()),
    url(r"^summary/", views.SummaryView.as_view()),
    url(r"^detail/(?P<pk>[0-9]+)", views.UserDetailView.as_view()),
]
