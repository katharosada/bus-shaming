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
    pass


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    pass


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    pass


@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    pass


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    pass


@admin.register(TripStop)
class TripStopAdmin(admin.ModelAdmin):
    pass


@admin.register(TripTimetable)
class TripTimetableAdmin(admin.ModelAdmin):
    pass
