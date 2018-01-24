"""busshaming URL Configuration"""

from django.conf.urls import include, url
from django.contrib import admin

from rest_framework_nested import routers

from busshaming import views
from busshaming import timetable_views

from .api import RouteViewSet, RouteDateModelViewSet

router = routers.DefaultRouter()
router.register(r'routes', RouteViewSet)
router.register(r'routedates', RouteDateModelViewSet)


urlpatterns = [
    url(r'^$', views.index),
    url(r'^timetable/route/(\d+)/date/(\d{8})', timetable_views.route_by_date),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', admin.site.urls),
]
