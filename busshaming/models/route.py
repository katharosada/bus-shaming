from django.db import models


class Route(models.Model):
    gtfs_route_id = models.CharField(max_length=200)
    feed_id = models.ForeignKey('Feed')
    agency_id = models.ForeignKey('Agency')
    route_short_name = models.CharField(max_length=200)
    route_long_name = models.CharField(max_length=200)
    route_desc = models.CharField(blank=True, null=True, max_length=500)
    route_url = models.CharField(blank=True, null=True, max_length=200)
    route_color = models.CharField(blank=True, null=True, max_length=7)
    route_text_color = models.CharField(blank=True, null=True, max_length=7)

    class Meta:
        unique_together = ('gtfs_route_id', 'feed_id')
