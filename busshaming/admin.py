from django.contrib import admin

from .models import (
    Agency,
    Feed,
    Route,
    Stop,
    Trip,
    TripStop,
    TripTimetable,
)


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ('id', 'gtfs_agency_id', 'name')
    ordering = ('name',)
    search_fields = ('gtfs_agency_id', 'name')


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    pass


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('gtfs_route_id', 'short_name', 'long_name')
    ordering = ('gtfs_route_id',)
    search_fields = ('gtfs_route_id', 'short_name', 'long_name')


@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    search_fields = ('gtfs_stop_id', 'name')
    list_filter = ('feed',)


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('gtfs_trip_id', 'trip_short_name', 'route')
    list_filter = ('route__gtfs_route_id',)
    ordering = ('route__gtfs_route_id', 'gtfs_trip_id')
    search_fields = ('gtfs_trip_id', 'route__gtfs_route_id', 'route__short_name')


@admin.register(TripStop)
class TripStopAdmin(admin.ModelAdmin):
    list_display = ('trip', 'sequence', 'stop')
    search_fields = ('trip__gtfs_trip_id', 'stop__gtfs_stop_id', 'stop__name')


@admin.register(TripTimetable)
class TripTimetableAdmin(admin.ModelAdmin):
    pass
