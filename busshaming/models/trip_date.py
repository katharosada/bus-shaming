from django.db import models


class TripDate(models.Model):
    trip = models.ForeignKey('Trip')
    date = models.DateField(db_index=True)
    added_from_realtime = models.BooleanField(default=False)

    # Denormalized start time from the first tripstop
    start_time = models.CharField(max_length=8, null=True, blank=True)

    # Stats about this trip
    has_stats = models.BooleanField(default=False)
    num_scheduled_stops = models.PositiveSmallIntegerField(null=True, blank=True)
    num_realtime_stops = models.PositiveSmallIntegerField(null=True, blank=True)

    start_delay = models.SmallIntegerField(null=True, blank=True)
    middle_delay = models.SmallIntegerField(null=True, blank=True)
    end_delay = models.SmallIntegerField(null=True, blank=True)
    max_delay = models.SmallIntegerField(null=True, blank=True)

    num_delay_stops = models.PositiveSmallIntegerField(null=True, blank=True)
    sum_delay = models.IntegerField(null=True, blank=True)
    sum_delay_squared = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('trip', 'date')

    def __str__(self):
        return f'Trip {self.trip.gtfs_trip_id} on {self.date}'
