import django
django.setup()

from busshaming.models import Trip


def main():
    for trip in Trip.objects.prefetch_related('stop_sequence'):
        count = trip.tripstop_set.count()
        if count != 0 and count != trip.stop_sequence.length:
            print(trip, count, trip.stop_sequence.length)


if __name__ == '__main__':
    main()
