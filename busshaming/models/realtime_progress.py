from django.db import models


class RealtimeProgress(models.Model):
    feed = models.ForeignKey('Feed')
    start_date = models.DateField()
    in_progress = models.DateTimeField(blank=True, null=True)
    last_processed_dump = models.CharField(max_length=50, blank=True, null=True)
    completed = models.BooleanField(default=False)
