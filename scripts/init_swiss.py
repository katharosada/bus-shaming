import os
import django
django.setup()

from busshaming.models import Feed, FeedTimetable


def main():
    feed = Feed.objects.filter(slug='swiss').first()
    if feed is None:
        print(f'Creating Swiss feed')
        feed = Feed(slug='swiss', name='Switzerland', timezone='Europe/Zurich')
        feed.realtime_feed_url = 'https://api.opentransportdata.swiss/gtfs-rt'
        feed.active = True
        feed.save()


if __name__ == '__main__':
    main()
