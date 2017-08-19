from django.db import models


class TripDate(models.Model):
    trip = models.ForeignKey('Trip')
    date = models.DateField(db_index=True)

    class Meta:
        unique_together = ('trip', 'date')

    def __str__(self):
        return f'Trip {self.trip.gtfs_trip_id} on {self.date}'

