import hashlib

from django.db import transaction
from busshaming.models import Route, StopSequence, TripStop


def upsert_stop_sequence(trip, sequence):
    key = ','.join(str(stop_id) for stop_id in sequence)
    keyhash = hashlib.sha256(key.encode('ascii')).hexdigest()
    with transaction.atomic():
        try:
            stop_sequence = StopSequence.objects.get(sequence_hash=keyhash, route_id=trip.route_id)
        except StopSequence.DoesNotExist:
            stop_sequence = StopSequence(sequence_hash=keyhash, stop_sequence=key, route_id=trip.route_id)
            stop_sequence.length = len(sequence)
            stop_sequence.direction = trip.direction
            print('Adding new stop sequence for trip ' + str(trip))

        if trip.trip_short_name:
            stop_sequence.trip_headsign = trip.trip_headsign
            stop_sequence.trip_short_name = trip.trip_short_name
            stop_sequence.direction = trip.direction
        elif stop_sequence.trip_short_name:
            trip.trip_short_name = stop_sequence.trip_short_name
            trip.trip_headsign = stop_sequence.trip_headsign
            trip.direction = stop_sequence.direction

        stop_sequence.save()
        trip.stop_sequence = stop_sequence
        trip.save()


def update_all_stop_sequences():
    print('Updating stop sequences')
    # For each Route, find all the trips and stops
    for route in Route.objects.all():
        trips = route.trip_set.filter(stop_sequence__isnull=True).all()
        for trip in trips:
            this_sequence = []
            trip_stops = TripStop.objects.filter(trip=trip).order_by('sequence')
            for trip_stop in trip_stops:
                this_sequence.append(trip_stop.stop_id)
            upsert_stop_sequence(trip, this_sequence)


def verify_stop_sequences(route_id):
    print('Checking stop sequences')
    # For each Route, find all the trips and stops
    ok = 0
    for route in Route.objects.filter(id=route_id).all():
        trips = route.trip_set.all()
        for trip in trips:
            this_sequence = []
            trip_stops = TripStop.objects.filter(trip=trip).order_by('sequence')
            prev = 0
            for trip_stop in trip_stops:
                if trip_stop.sequence != prev + 1:
                    print('OH NOES!')
                    print(trip)
                    raise 'oh no'
                prev += 1
                this_sequence.append(trip_stop.stop_id)
            ok += 1
    print(f'{ok} were ok')
