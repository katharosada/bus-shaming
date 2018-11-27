from django.db import models

from busshaming.enums import ScheduleRelationship


class RouteStopDay(models.Model):
    route = models.ForeignKey('Route')
    stop = models.ForeignKey('Stop')
    date = models.DateField(db_index=True)
    
    scheduled_bus_count = models.PositiveSmallIntegerField()
    realtime_bus_count = models.PositiveSmallIntegerField()

    # How long you have to wait if you show up 5min before scheduled time.
    # Only applies if there's more than one bus (from first bus to last bus)
    schedule_wait_time_seconds_total = models.PositiveIntegerField()
    # Per scheduled bus
    schedule_wait_time_seconds_avg = models.PositiveIntegerField()

    class Meta:
        unique_together = ('route', 'stop', 'date')
