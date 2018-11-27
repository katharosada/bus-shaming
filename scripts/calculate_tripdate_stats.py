import django
import time

django.setup()


from busshaming.data_processing.calculate_stats import calculate_stats_for_day
from busshaming.models import Feed, RealtimeProgress


def get_next_realtime_progress(feed_slug):
    feed = Feed.objects.get(slug=feed_slug)
    return RealtimeProgress.objects.filter(feed=feed, completed=True, stats_completed=False, in_progress__isnull=True).order_by('start_date').first()


def main():
    while True:
        realtime_progress = get_next_realtime_progress('nsw-buses')
        if realtime_progress is None:
            print('No available days to process')
            time.sleep(30)
        print(realtime_progress)
        success = realtime_progress.take_processing_lock(allow_completed=True)
        if not success:
            print('Failed to get realtime lock. Bailing out.')
            continue
        try:
            calculate_stats_for_day(realtime_progress.start_date)
            realtime_progress.set_stats_completed()
        finally:
            realtime_progress.release_processing_lock()


if __name__ == '__main__':
    main()
