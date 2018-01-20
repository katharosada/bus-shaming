import django
django.setup()

from busshaming.models import Trip


def main():
    count = 0
    clones = 0
    for trip in Trip.objects.filter(added_from_realtime=True):
        # Clear all TripStops
        trip.tripstop_set.all().delete()
        trip.stop_sequence = None
        trip.save()
        count += 1

        if '_' in trip.gtfs_trip_id:
            # Re-clone all the trip stops from the original trip
            original_trip_id = trip.gtfs_trip_id.split('_')[0]
            if original_trip_id != '':
                original_trip = Trip.objects.filter(gtfs_trip_id=original_trip_id, added_from_realtime=False).order_by('-version').first()
                if original_trip is not None:
                    clones += 1
                    print('cloning', original_trip)
                    for tripstop in original_trip.tripstop_set.all():
                        tripstop.clone_to_new_trip(trip)
    print('count', count)
    print('clones', clones)


if __name__ == '__main__':
    main()
