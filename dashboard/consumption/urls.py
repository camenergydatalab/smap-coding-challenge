from django.urls import path
from . import views

urlpatterns = [
    path('', views.SummaryView.as_view(), name='summary'),
    path('summary', views.SummaryView.as_view(), name='summary'),
    path('detail/<int:user_id>/', views.detail, name="detail"),
]
