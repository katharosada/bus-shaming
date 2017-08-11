from django.db import models


class Agency(models.Model):
    gtfs_agency_id = models.CharField(max_length=200)
    feed_id = models.ForeignKey('Feed')
    name = models.CharField(max_length=200)

    class Meta:
        unique_together = ('gtfs_agency_id', 'feed_id')
