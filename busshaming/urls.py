"""busshaming URL Configuration"""

from django.conf.urls import include, url
from django.contrib import admin

from busshaming import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^fetch_timetable', views.fetch_timetable, name='fetch_timetable'),
    url(r'^admin/', admin.site.urls),
    url('', include('django_prometheus.urls')),
]
