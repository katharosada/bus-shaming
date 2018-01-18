from django.contrib import admin

from .models import (
    Agency,
    Feed,
    FeedTimetable,
    RealtimeEntry,
    RealtimeProgress,
    Route,
    Stop,
    StopSequence,
    Trip,
    TripDate,
    TripStop,
)


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ('id', 'gtfs_agency_id', 'name')
    ordering = ('name',)
    search_fields = ('gtfs_agency_id', 'name')


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'name', 'realtime_feed_url', 'active')


@admin.register(FeedTimetable)
class FeedTimetableAdmin(admin.ModelAdmin):
    list_display = ('id', 'feed', 'timetable_url', 'fetch_last_modified', 'last_processed_zip')
    ordering = ('id',)


@admin.register(RealtimeProgress)
class RealtimeProgressAdmin(admin.ModelAdmin):
    list_display = ('feed', 'start_date', 'last_processed_dump', 'in_progress', 'completed')
    ordering = ('start_date',)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('gtfs_route_id', 'short_name', 'long_name')
    ordering = ('gtfs_route_id',)
    search_fields = ('gtfs_route_id', 'short_name', 'long_name')


@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    search_fields = ('gtfs_stop_id', 'name')
    list_filter = ('feed',)


@admin.register(StopSequence)
class StopSequenceAdmin(admin.ModelAdmin):
    list_display = ('trip_headsign', 'trip_short_name', 'direction', 'length')
    search_fields = ('trip_headsign', 'trip_short_name', 'length')


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('gtfs_trip_id', 'trip_short_name', 'route', 'added_from_realtime', 'scheduled')
    list_filter = ('added_from_realtime', 'scheduled')
    ordering = ('route__gtfs_route_id', 'gtfs_trip_id')
    search_fields = ('gtfs_trip_id', 'route__gtfs_route_id', 'route__short_name')


@admin.register(TripDate)
class TripDateAdmin(admin.ModelAdmin):
    list_display = ('trip', 'date', 'added_from_realtime')
    list_filter = ('date', 'added_from_realtime')
    raw_id_fields = ('trip',)
    search_fields = ('trip__gtfs_trip_id',)


@admin.register(TripStop)
class TripStopAdmin(admin.ModelAdmin):
    list_display = ('trip', 'sequence', 'stop', 'arrival_time')
    search_fields = ('trip__gtfs_trip_id', 'stop__gtfs_stop_id', 'stop__name')
    raw_id_fields = ('trip', 'stop')
