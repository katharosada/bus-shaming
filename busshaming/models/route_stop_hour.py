from django.db import models

from busshaming.enums import ScheduleRelationship


class RouteStopHour(models.Model):
    route = models.ForeignKey('Route')
    stop = models.ForeignKey('Stop')
    date = models.DateField(db_index=True)
    hour = models.PositiveSmallIntegerField(db_index=True)

    scheduled_bus_count = models.PositiveSmallIntegerField()
    realtime_bus_count = models.PositiveSmallIntegerField()

    expected_wait_next_day = models.BooleanField(default=False)
    realtime_wait_next_day = models.BooleanField(default=False)
    expected_random_wait_time_seconds = models.IntegerField(null=True, blank=True)
    realtime_random_wait_time_seconds = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('route', 'stop', 'date', 'hour')
