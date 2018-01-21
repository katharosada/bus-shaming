from django.db import models


class TripStop(models.Model):
    trip = models.ForeignKey('Trip')
    stop = models.ForeignKey('Stop')
    sequence = models.IntegerField()
    arrival_time = models.CharField(max_length=8)
    departure_time = models.CharField(max_length=8)
    timepoint = models.BooleanField()

    class Meta:
        unique_together = ('trip', 'stop', 'sequence')

    def __str__(self):
        return f'Trip {self.trip.gtfs_trip_id} stop {self.sequence} ({self.stop_id})'

    def clone_to_new_trip(self, new_trip):
        new_tripstop = TripStop(
                trip=new_trip,
                stop=self.stop,
                sequence=self.sequence,
                arrival_time=self.arrival_time,
                departure_time=self.departure_time,
                timepoint=self.timepoint)
        new_tripstop.save()
