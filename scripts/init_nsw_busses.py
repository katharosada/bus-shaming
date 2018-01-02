import os
import django
django.setup()

from busshaming.models import Feed, FeedTimetable


SCHEDULE_URL = 'https://api.transport.nsw.gov.au/v1/gtfs/schedule/'
SCHEDULE_SUFFIXES = [
    'buses/SMBSC001',
    'buses/SMBSC002',
    'buses/SMBSC003',
    'buses/SMBSC004',
    'buses/SMBSC005',
    'buses/SMBSC006',
    'buses/SMBSC007',
    'buses/SMBSC008',
    'buses/SMBSC009',
    'buses/SMBSC010',
    'buses/SMBSC012',
    'buses/SMBSC013',
    'buses/SMBSC014',
    'buses/SMBSC015',
    'buses/Nightride',
    'buses/Major_Event',
    'buses/OSMBSC001',
    'buses/OSMBSC002',
    'buses/OSMBSC003',
    'buses/OSMBSC004',
    'buses/OSMBSC005',
    'buses/OSMBSC006',
    'buses/OSMBSC007',
    'buses/OSMBSC008',
    'buses/OSMBSC009',
    'buses/OSMBSC010',
    'buses/OSMBSC011',
    'buses/OSMBSC012',
    'buses/NISC001',
]


def main():
    feed = Feed.objects.filter(slug='nsw-buses').first()
    if feed is None:
        print(f'Creating NSW busses feed')
        feed = Feed(slug='nsw-buses', name='Transport NSW Buses', timezone='Australia/Sydney')
        feed.realtime_feed_url = 'https://api.transport.nsw.gov.au/v1/gtfs/realtime/buses/'
        feed.active = True
        feed.save()

    existing_timetable_urls = set(FeedTimetable.objects.filter(feed=feed).values_list('timetable_url', flat=True))
    for suffix in SCHEDULE_SUFFIXES:
        url = os.path.join(SCHEDULE_URL, suffix)
        if url not in existing_timetable_urls:
            print(f'Adding {url}')
            ft = FeedTimetable(feed=feed, timetable_url=url)
            ft.save()


if __name__ == '__main__':
    main()
