from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.summary),
    url(r'^summary/', views.summary),
    url(r'^(?P<user_id>[0-9]+)/', views.detail),
]
