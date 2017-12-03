from django.db import models


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

    class Meta:
        unique_together = ('gtfs_trip_id', 'version', 'route')

    def __str__(self):
        return f'Trip {self.gtfs_trip_id} v{self.version} (Route {self.route.short_name})'
