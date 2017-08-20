"""busshaming URL Configuration"""

from django.conf.urls import include, url
from django.contrib import admin

from busshaming import views
from busshaming import timetable_views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^fetch_timetable', views.fetch_timetable, name='fetch_timetable'),
    url(r'^timetable/route/(\d+)/date/(\d{8})', timetable_views.route_by_date),
    url(r'^admin/', admin.site.urls),
    url('', include('django_prometheus.urls')),
]
