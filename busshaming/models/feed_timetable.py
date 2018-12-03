from django.db import models


class FeedTimetable(models.Model):
    feed = models.ForeignKey('Feed')
    timetable_url = models.URLField()
    fetch_last_modified = models.CharField(max_length=50, blank=True, null=True)
    last_processed_zip = models.CharField(max_length=50, blank=True, null=True)
    active = models.BooleanField(default=True)
    processed_watermark = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('feed', 'timetable_url')

    def __str__(self):
        return f'{self.feed.slug} - {self.timetable_url}'
