from django.db import models


class Feed(models.Model):
    slug = models.SlugField()
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    timezone = models.CharField(max_length=200)
    realtime_feed_url = models.URLField()
    active = models.BooleanField()
    last_processed_dump = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f'{self.slug} - {self.name}'
