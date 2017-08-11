from django.db import models


class Stop(models.Model):
    gtfs_stop_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
