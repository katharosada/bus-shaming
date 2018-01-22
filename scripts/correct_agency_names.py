import django
django.setup()

from busshaming.models import Feed, Agency

AGENCY_NAMES = {
    '2436': 'Hillsbus',
    '2440': 'State Transit Sydney',
    '2441': 'State Transit Sydney',
}


def main():
    feed = Feed.objects.get(slug='nsw-buses')
    for agency_id in AGENCY_NAMES:
        Agency.objects.filter(feed=feed, gtfs_agency_id=agency_id).update(name=AGENCY_NAMES[agency_id])


if __name__ == '__main__':
    main()
