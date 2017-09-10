"""busshaming URL Configuration"""

from django.conf.urls import url
from django.contrib import admin

from busshaming import views
from busshaming import timetable_views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^timetable/route/(\d+)/date/(\d{8})', timetable_views.route_by_date),
    url(r'^admin/', admin.site.urls),
]
