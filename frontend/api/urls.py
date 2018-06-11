from django.conf.urls import url, include
from api import views


urlpatterns = [
    url(r'^consumers/(?P<consumer_type>[a-zA-Z_]+)$', views.ConsumerList.as_view()),
    url(r'^consumers/', views.ConsumerList.as_view()),
    url(r'^consumer/(?P<consumer_id>[0-9]+)$', views.ConsumerDetail.as_view()),
    url(r'^consumer/', views.ConsumerDetail.as_view()),
    url(r'^consumer_types/', views.ConsumerTypes.as_view()),
    url(r'^monthly_statistics/(?P<consumer_id>[0-9]+)$', views.MonthlyStatisticsApi.as_view()),

]
