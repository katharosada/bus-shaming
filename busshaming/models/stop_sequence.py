
from django.db import models


class StopSequence(models.Model):
    sequence_hash = models.CharField(max_length=64)
    stop_sequence = models.TextField()
    length = models.SmallIntegerField()
    route = models.ForeignKey('Route')
    trip_headsign = models.CharField(max_length=200, blank=True, null=True)
    trip_short_name = models.CharField(max_length=200, blank=True, null=True)
    direction = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sequence_hash', 'route')

    def __str__(self):
        return f'Stop Sequence {self.trip_headsign} {self.trip_short_name}'
