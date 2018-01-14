from django.db import models
from django.db import transaction


class Trip(models.Model):
    gtfs_trip_id = models.CharField(max_length=200)
    version = models.IntegerField(default=0)
    active = models.BooleanField()
    route = models.ForeignKey('Route')
    stop_sequence = models.ForeignKey('StopSequence', blank=True, null=True)
    trip_headsign = models.CharField(max_length=200, blank=True, null=True)
    trip_short_name = models.CharField(max_length=200, blank=True, null=True)
    direction = models.SmallIntegerField()
    wheelchair_accessible = models.BooleanField()
    bikes_allowed = models.BooleanField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    added_from_realtime = models.BooleanField(default=False)
    scheduled = models.BooleanField(default=True)

    class Meta:
        unique_together = ('gtfs_trip_id', 'version', 'route')

    def __str__(self):
        return f'Trip {self.gtfs_trip_id} v{self.version} (Route {self.route.short_name})'

    def clone_to_unscheduled(self, new_gtfs_trip_id):
        with transaction.atomic():
            self.refresh_from_db()
            new_trip = Trip(
                    gtfs_trip_id=new_gtfs_trip_id,
                    version=0,
                    active=True,
                    route=self.route,
                    stop_sequence=self.stop_sequence,
                    trip_headsign=self.trip_headsign,
                    trip_short_name=self.trip_short_name,
                    direction=self.direction,
                    wheelchair_accessible=self.wheelchair_accessible,
                    bikes_allowed=self.bikes_allowed,
                    added_from_realtime=True,
                    scheduled=False)
            new_trip.save()
            for tripstop in self.tripstop_set.all():
                tripstop.clone_to_new_trip(new_trip)
        return new_trip

