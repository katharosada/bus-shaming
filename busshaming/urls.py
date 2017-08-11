"""busshaming URL Configuration"""

from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('', include('django_prometheus.urls')),
]
