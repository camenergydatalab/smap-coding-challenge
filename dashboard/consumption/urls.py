from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.summary),
    url(r'^summary/', views.summary),
    url(r'^detail/', views.detail),
    url(r'api/consumption_grouped_by_area', views.ConsumptionGroupedByArea.as_view())
]
