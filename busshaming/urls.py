"""busshaming URL Configuration"""

from django.conf.urls import include, url
from django.contrib import admin

from rest_framework_nested import routers

from busshaming import views
from busshaming import timetable_views

from .api import RouteViewSet, StopSequenceViewSet, TripDateViewSet, TripViewSet, RouteDateViewSet, RouteDateTripViewSet, RealtimeEntryViewSet

router = routers.DefaultRouter()
router.register(r'routes', RouteViewSet)
router.register(r'trips', TripViewSet)
router.register(r'sequences', StopSequenceViewSet)
router.register(r'tripdates', TripDateViewSet)
router.register(r'realtimeentrys', RealtimeEntryViewSet)

route_router = routers.NestedSimpleRouter(router, 'routes', lookup='route')
route_router.register('dates', RouteDateViewSet, base_name='dates')

routedate_router = routers.NestedSimpleRouter(route_router, 'dates', lookup='date')
routedate_router.register('trips', RouteDateTripViewSet, base_name='trips')


urlpatterns = [
    url(r'^$', views.index),
    url(r'^timetable/route/(\d+)/date/(\d{8})', timetable_views.route_by_date),
    url(r'^api/', include(router.urls)),
    url(r'^api/', include(route_router.urls)),
    url(r'^api/', include(routedate_router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', admin.site.urls),
]
