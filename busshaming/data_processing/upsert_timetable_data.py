import csv
import io
from datetime import datetime, timedelta
from collections import defaultdict

from django.contrib.gis.geos import Point

from busshaming.models import Agency, Route, Stop, Trip, TripDate, TripStop


DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']


def process_agencies(feed, csvreader):
    print('Processing agencies')
    for row in csvreader:
        gtfs_agency_id = row['agency_id']
        agency = Agency.objects.filter(feed=feed, gtfs_agency_id=gtfs_agency_id).first()
        if agency is None:
            agency = Agency(feed=feed, gtfs_agency_id=gtfs_agency_id)
        agency.name = row['agency_name']
        agency.save()


def process_routes(feed, csvreader):
    print('Processing routes')

    existing = {}
    for route in Route.objects.filter(feed=feed):
        existing[route.gtfs_route_id] = route

    agencies = {}
    for agency in Agency.objects.filter(feed=feed):
        agencies[agency.gtfs_agency_id] = agency

    for route_row in csvreader:
        gtfs_route_id = route_row['route_id']
        changed = False
        if gtfs_route_id in existing:
            route = existing[gtfs_route_id]
        else:
            changed = True
            route = Route(feed=feed, gtfs_route_id=gtfs_route_id)
            print('New route {route}')
        gtfs_agency_id = route_row['agency_id']
        values = {}
        values['agency_id'] = agencies[gtfs_agency_id].id
        values['short_name'] = route_row['route_short_name']
        values['long_name'] = route_row['route_long_name']
        values['description'] = route_row['route_desc']
        values['url'] = route_row.get('route_url', '')
        values['color'] = route_row['route_color']
        values['text_color'] = route_row['route_text_color']

        for value in values:
            prev = getattr(route, value)
            if prev != values[value]:
                setattr(route, value, values[value])
                changed = True
                print(f'Route {route} changed {value}')
        if changed:
            route.save()


def process_trip_dates(csvreader):
    print('Processing trip dates')
    result = defaultdict(list)
    limit = datetime.now().date() + timedelta(days=14)
    today = datetime.now().date()
    for row in csvreader:
        start_date = datetime.strptime((row['start_date']), '%Y%m%d').date()
        end_date = datetime.strptime((row['end_date']), '%Y%m%d').date()
        days = set()
        for i, day in enumerate(DAYS_OF_WEEK):
            if row[day] == '1':
                days.add(i)
        cur_date = start_date
        if cur_date < today:
            cur_date = today
        while cur_date <= end_date and cur_date < limit:
            if cur_date.weekday() in days:
                # Add to set of days.
                result[row['service_id']].append(cur_date)
            cur_date += timedelta(days=1)
    return result


def process_trips(feed, all_trip_dates, trip_stops, csvreader):
    print('Processing trips')
    existing = {}
    for trip in Trip.objects.filter(route__feed=feed).order_by('version'):
        existing[trip.gtfs_trip_id] = trip

    routes = {}
    for route in Route.objects.filter(feed=feed):
        routes[route.gtfs_route_id] = route

    current_trip_dates = defaultdict(dict)
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    for trip_date in TripDate.objects.filter(trip__route__feed=feed, date__gte=yesterday):
        current_trip_dates[trip_date.trip_id][trip_date.date] = trip_date

    for trip_row in csvreader:
        gtfs_route_id = trip_row['route_id']
        gtfs_trip_id = trip_row['trip_id']
        # Should always exist
        route = routes.get(gtfs_route_id)
        changed = False

        trip = existing.get(gtfs_trip_id, None)
        if trip is not None and gtfs_trip_id in trip_stops:
            # The trip stops have changed. Create a new version of the trip.
            new_version = trip.version + 1
            trip = Trip(route=route, gtfs_trip_id=gtfs_trip_id, version=new_version)
            changed = True
        if trip is None:
            changed = True
            trip = Trip(route=route, gtfs_trip_id=gtfs_trip_id)

        values = {}
        values['active'] = True  # If it's in the feed it's active
        values['direction'] = int(trip_row['direction_id'])
        values['trip_headsign'] = trip_row['trip_headsign']
        values['trip_short_name'] = trip_row.get('trip_short_name', '')
        if 'route_direction' in trip_row and 'trip_short_name' not in trip_row:
            values['trip_short_name'] = trip_row['route_direction']
        values['wheelchair_accessible'] = trip_row['wheelchair_accessible'] == '1'
        values['bikes_allowed'] = trip_row.get('bikes_allowed', '') == '1'
        values['notes'] = trip_row.get('trip_note', '')

        for value in values:
            prev = getattr(trip, value)
            if prev != values[value]:
                setattr(trip, value, values[value])
                changed = True
        if changed:
            trip.save()

        if gtfs_trip_id in trip_stops:
            to_create = []
            for tripstop_data in trip_stops[gtfs_trip_id]:
                to_create.append(TripStop(trip=trip, **tripstop_data))
            TripStop.objects.bulk_create(to_create)

        trip_dates = all_trip_dates[trip_row['service_id']]
        old_trip_dates = current_trip_dates[trip.id]
        for new_trip_date in trip_dates:
            old_trip_date = old_trip_dates.pop(new_trip_date, None)
            if old_trip_date is None:
                TripDate(trip=trip, date=new_trip_date).save()
        for old_trip_date in old_trip_dates.values():
            # Don't delete trips older than the new dump just because they aren't listed anymore.
            if old_trip_date.date > today:
                old_trip_date.delete()


def process_stops(feed, csvreader):
    print('Processing stops')
    existing = {}
    for stop in Stop.objects.filter(feed=feed):
        existing[stop.gtfs_stop_id] = stop

    for row in csvreader:
        gtfs_stop_id = row['stop_id']
        stop = existing.get(gtfs_stop_id, None)
        changed = False
        values = {}
        values['name'] = row['stop_name']
        x = float(row['stop_lon'])
        y = float(row['stop_lat'])
        values['position'] = Point(x, y, srid=4326)
        if stop is None:
            stop = Stop(feed=feed, gtfs_stop_id=gtfs_stop_id)
            changed = True
        for value in values:
            prev = getattr(stop, value)
            if prev != values[value]:
                setattr(stop, value, values[value])
                changed = True
        if changed:
            stop.save()


def process_stop_times(feed, csvreader):
    print('Processing stop times')
    stops = {}
    for stop in Stop.objects.filter(feed=feed):
        stops[stop.gtfs_stop_id] = stop

    trips = {}
    for trip in Trip.objects.filter(route__feed=feed):
        trips[trip.id] = trip

    existing = defaultdict(lambda: defaultdict(list))
    for tripstop in TripStop.objects.filter(stop__feed=feed).order_by('trip_id', 'sequence'):
        trip = trips[tripstop.trip_id]
        existing[trip.gtfs_trip_id][trip.version].append(tripstop)

    # If the stop times have changed we want to create a new trip version for them
    # later on when we create the trips. Otherwise we don't care.
    stop_sets = defaultdict(list)  # {gtfs_trip_id: [stop1, stop2, ...]}

    for row in csvreader:
        gtfs_trip_id = row['trip_id']
        new_stop = {
            'stop': stops[row['stop_id']],
            'sequence': int(row['stop_sequence']),
            'arrival_time': row['arrival_time'],
            'departure_time': row['departure_time'],
            'timepoint': row['timepoint'] == 1
        }
        stop_sets[gtfs_trip_id].append(new_stop)

    new_stop_sets = {}
    for gtfs_trip_id in stop_sets:
        stop_sets[gtfs_trip_id].sort(key=lambda stop: stop['sequence'])
        existing_stopsets = existing[gtfs_trip_id]
        existing_stops = None
        if len(existing_stopsets) != 0:
            latest_version = sorted(existing_stopsets)[-1]
            existing_stops = existing_stopsets[latest_version]
            # TODO: Add to new_stop_sets only if changed
            if len(existing_stops) != len(stop_sets[gtfs_trip_id]):
                print('MISMATCH', existing_stops[0].trip_id)
                new_stop_sets[gtfs_trip_id] = stop_sets[gtfs_trip_id]
            else:
                mismatch = False
                for new_stop, existing_stop in zip(stop_sets[gtfs_trip_id], existing_stops):
                    if new_stop['sequence'] != existing_stop.sequence:
                        print(f'MISMATCH sequence {gtfs_trip_id} {new_stop["sequence"]} {existing_stop.sequence}')
                        mismatch = True
                    elif new_stop['stop'].id != existing_stop.stop_id:
                        print(f'MISMATCH stop_id {gtfs_trip_id}')
                        mismatch = True
                    elif new_stop['arrival_time'] != existing_stop.arrival_time:
                        print(f'MISMATCH arrival time {gtfs_trip_id}')
                        mismatch = True
                    elif new_stop['departure_time'] != existing_stop.departure_time:
                        print(f'MISMATCH departure time {gtfs_trip_id}')
                        mismatch = True
                if mismatch:
                    print('Intending to create new trip version for {gtfs_trip_id}')
                    new_stop_sets[gtfs_trip_id] = stop_sets[gtfs_trip_id]
        else:
            print('Trip {} did not previously have stops'.format(gtfs_trip_id))
            # this trip has no stops already so we don't need to compare
            new_stop_sets[gtfs_trip_id] = stop_sets[gtfs_trip_id]
    return new_stop_sets


def process_zip(feed, zfile):
    process_agencies(feed, csv.DictReader(io.TextIOWrapper(zfile.open('agency.txt'))))
    process_routes(feed, csv.DictReader(io.TextIOWrapper(zfile.open('routes.txt'))))
    process_stops(feed, csv.DictReader(io.TextIOWrapper(zfile.open('stops.txt'))))
    trip_dates = process_trip_dates(csv.DictReader(io.TextIOWrapper(zfile.open('calendar.txt'))))
    trip_stops = process_stop_times(feed, csv.DictReader(io.TextIOWrapper(zfile.open('stop_times.txt'))))
    process_trips(feed, trip_dates, trip_stops, csv.DictReader(io.TextIOWrapper(zfile.open('trips.txt'))))
    return True
