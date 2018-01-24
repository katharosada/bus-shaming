from datetime import datetime, timedelta

from django.db import models


class Route(models.Model):
    gtfs_route_id = models.CharField(max_length=200)
    feed = models.ForeignKey('Feed')
    agency = models.ForeignKey('Agency')
    short_name = models.CharField(max_length=200)
    long_name = models.CharField(max_length=200)
    description = models.CharField(blank=True, null=True, max_length=500)
    route_url = models.CharField(blank=True, null=True, max_length=200)
    color = models.CharField(blank=True, null=True, max_length=7)
    text_color = models.CharField(blank=True, null=True, max_length=7)

    class Meta:
        unique_together = ('gtfs_route_id', 'feed')

    def __str__(self):
        return f'{self.gtfs_route_id} - {self.short_name}'

    def recent_dates(self):
        start = datetime.now().date() - timedelta(days=14)

        return self.routedate_set.filter(date__gte=start)
