from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path('', views.summary, name='summary'),
    path('summary/', views.summary, name='summary'),
    path('detail/<int:user_id>/', views.detail, name='detail'),
]
