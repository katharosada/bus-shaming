import django
import time
import cProfile
from datetime import timedelta

django.setup()

from django.db import transaction

from busshaming.data_processing import process_realtime_dumps

from busshaming.models import Feed, FeedTimetable, RealtimeProgress


def new_realtime_progress(feed, start_date):
    progress = RealtimeProgress(feed=feed, start_date=start_date)
    progress.save()
    return progress


def find_available_work(feed_slug):
    feed = Feed.objects.get(slug=feed_slug)
    latest_watermark = get_latest_watermark(feed)

    # Get all logged days of processing
    with transaction.atomic():
        progresses = list(RealtimeProgress.objects.filter(feed=feed).order_by('start_date'))

        if len(progresses) == 0:
            # TODO: Add logic to find the first realtime dump file on S3
            raise NotImplementedError()

        # Find first day which is either missing or not complete and not in progress
        if progresses[0].in_progress is None and not progresses[0].completed:
            return progresses[0]
        prev_start = progresses[0].start_date
        for progress_day in progresses[1:]:
            if progress_day.start_date != prev_start + timedelta(days=1):
                return new_realtime_progress(feed, prev_start + timedelta(days=1))
            if not progress_day.completed and progress_day.in_progress is None:
                return progress_day
            prev_start = progress_day.start_date

        if prev_start >= latest_watermark.date():
            # Need to wait until timetable catches up.
            print(f'Latest watermark is {latest_watermark}. Holding off on realtime.')
            return None
        return new_realtime_progress(feed, prev_start + timedelta(days=1))

def get_latest_watermark(feed):
    feed_timetable = FeedTimetable.objects.filter(feed=feed).order_by('processed_watermark').first()
    return feed_timetable.processed_watermark


if __name__ == '__main__':
    #cProfile.run('process_realtime_dumps.process_next(10)', filename='output.txt')

    while True:
        progress = find_available_work('nsw-buses')
        if progress is not None:
            process_realtime_dumps.process_next(progress, 15)
        time.sleep(2)
