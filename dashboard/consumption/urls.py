from django.urls import path

from . import views

app_name = "consumption"

urlpatterns = [
    path('', views.summary),
    path('summary/', views.summary, name="summary"),
    path('detail/<int:user_id>/', views.detail, name="detail"),
]
