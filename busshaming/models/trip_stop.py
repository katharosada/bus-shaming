from django.db import models


class TripStop(models.Model):
    trip_id = models.ForeignKey('Trip')
    stop_id = models.ForeignKey('Stop')
    sequence = models.IntegerField()
    arrival_time = models.CharField(max_length=5)
    departure_time = models.CharField(max_length=5)
    timepoint = models.BooleanField()
