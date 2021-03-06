from django.db import models


class Agency(models.Model):
    gtfs_agency_id = models.CharField(max_length=200)
    feed = models.ForeignKey('Feed')
    name = models.CharField(max_length=200)

    class Meta:
        unique_together = ('gtfs_agency_id', 'feed')

    def __str__(self):
        return f'{self.feed.slug} - {self.gtfs_agency_id} ({self.name})'
