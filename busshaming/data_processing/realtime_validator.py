from datetime import datetime, date, timezone, timedelta
from collections import defaultdict

from busshaming.models import TripDate, Trip, Route, RealtimeEntry, TripStop

START_DATE = date(2017, 9, 22)
#END_DATE = date(2017, 10, 17)
END_DATE = date(2017, 9, 25)


def validate_route(route_id):
    trip_date_stats = {
        'trip_dates': 0,
        'trip_added_from_realtime': 0,
        'trip_dates_added_from_realtime': 0,
        'trip_dates_perfect_match': 0,
        'trip_dates_no_realtime': 0,
        'trip_dates_stops_dont_match': 0,
        'trip_dates_missing_stops_from_realtime': 0,
        'trip_dates_with_realtime_missing_stops': 0,
    }

    trip_dates_added_from_realtime = []
    trip_dates_missing_all_realtime = []

    missing_stop_sequence = defaultdict(int)

    all_tripstops = defaultdict(list)
    for tripstop in TripStop.objects.filter(trip__route_id=route_id).order_by('sequence'):
        all_tripstops[tripstop.trip_id].append(tripstop)

    test_date = START_DATE
    while test_date <= END_DATE:
        print(test_date)
        trip_dates = TripDate.objects.filter(trip__route_id=route_id, date=test_date).prefetch_related('realtimeentry_set', 'trip')
        for trip_date in trip_dates:
            print(trip_date)
            trip_date_stats['trip_dates'] += 1
            if trip_date.added_from_realtime:
                trip_date_stats['trip_dates_added_from_realtime'] += 1
                trip_dates_added_from_realtime.append(trip_date)
            if trip_date.trip.added_from_realtime:
                trip_date_stats['trip_added_from_realtime'] += 1
                continue
            trip_stops = all_tripstops[trip_date.trip_id]
            realtimes = list(trip_date.realtimeentry_set.all())
            realtimes.sort(key=lambda rt: rt.sequence)
            trip_stops.sort(key=lambda ts: ts.sequence)
            trip_stop_i = 0
            realtime_i = 0
            trip_date_missing_stops = False
            realtime_missing_stops = False
            stop_mismatch = False
            if len(realtimes) == 0:
                trip_date_stats['trip_dates_no_realtime'] += 1
                trip_dates_missing_all_realtime.append(trip_date)
            else:
                while trip_stop_i < len(trip_stops) and realtime_i < len(realtimes):
                    ts = trip_stops[trip_stop_i]
                    r = realtimes[realtime_i]
                    if ts.sequence == r.sequence:
                        if ts.stop_id != r.stop_id:
                            raise 'OMG stop mismatch'
                            stop_mismatch = True
                        trip_stop_i += 1
                        realtime_i += 1
                    else:
                        if ts.sequence < r.sequence:
                            trip_stop_i += 1
                            realtime_missing_stops = True
                        else:
                            realtime_i += 1
                            trip_date_missing_stops = True
                            missing_stop_sequence[r.sequence] += 1
                if stop_mismatch:
                    trip_date_stats['trip_dates_stops_dont_match'] += 1
                if trip_date_missing_stops:
                    trip_date_stats['trip_dates_missing_stops_from_realtime'] += 1
                if realtime_missing_stops:
                    trip_date_stats['trip_dates_with_realtime_missing_stops'] += 1
                if not stop_mismatch and not trip_date_missing_stops and not realtime_missing_stops:
                    trip_date_stats['trip_dates_perfect_match'] += 1
        test_date += timedelta(days=1)
    for stat in trip_date_stats:
        print(f'{stat}: {trip_date_stats[stat]}')
    for seq in missing_stop_sequence:
        print(f'Sequence: {seq}, count: {missing_stop_sequence[seq]}')

    print('Trip dates added from realtime:')
    for td in trip_dates_added_from_realtime:
        print(td)
    print('Trip dates missing all realtime data:')
    for td in trip_dates_missing_all_realtime:
        print(td)


