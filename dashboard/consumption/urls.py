from django.conf.urls import url
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    url(r'^$', RedirectView.as_view(url="summary", query_string=True)),
    url(r'^summary/$', views.summary, name="summary"),
    url(r'^detail/(\d+)$', views.detail, name="detail"),
    url(r'^query$', views.query, name="query"),
]
