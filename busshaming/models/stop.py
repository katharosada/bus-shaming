from django.db import models


class Stop(models.Model):
    feed = models.ForeignKey('Feed')
    gtfs_stop_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)

    class Meta:
        unique_together = ('feed', 'gtfs_stop_id')

    def __str__(self):
        return f'{self.gtfs_stop_id} - {self.name}'
