from datetime import datetime, time, timedelta, timezone
import pytz

from django.db import models
from django.db import transaction

from busshaming.models import Feed


class RealtimeProgress(models.Model):
    feed = models.ForeignKey('Feed')
    start_date = models.DateField()
    in_progress = models.DateTimeField(blank=True, null=True)
    last_processed_dump = models.CharField(max_length=50, blank=True, null=True)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = (('feed', 'start_date'),)

    def take_processing_lock(self):
        with transaction.atomic():
            self.refresh_from_db()
            if self.completed:
                return False
            if self.in_progress is None:
                self.in_progress = datetime.utcnow().replace(tzinfo=timezone.utc)
                self.save()
                return True
            return False

    def update_progress(self, last_processed_dump, completed):
        with transaction.atomic():
            self.refresh_from_db()
            assert self.in_progress is not None
            self.last_processed_dump = last_processed_dump
            self.completed = completed
            self.save()

    def release_processing_lock(self):
        with transaction.atomic():
            self.refresh_from_db()
            self.in_progress = None
            self.save()

    def start_time(self):
        # Midnight in the feed timezone, translated to UTC
        dt = datetime.combine(self.start_date, time(0))
        feed_tz = pytz.timezone(self.feed.timezone)
        dt = feed_tz.localize(dt)
        return dt.astimezone(timezone.utc)

    def end_time(self):
        # 36h after the start time
        return self.start_time() + timedelta(hours=36)

    def __str__(self):
        return f'Progress shard {self.start_date} ({self.feed})'
