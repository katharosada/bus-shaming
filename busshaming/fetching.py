import csv
import io
import os
import zipfile
from datetime import datetime
from collections import defaultdict
from pathlib import Path

import django
import pytz
import requests


django.setup()

from busshaming.models import Agency, Feed, Route, Stop, Trip, TripStop


TMP_FILE_PATH = Path('./timetable.zip')
GTFS_API_KEY = os.environ.get('TRANSPORT_NSW_API_KEY')
GTFS_SCHEDULE_URL = 'https://api.transport.nsw.gov.au/v1/gtfs/schedule/buses/'
FEED_TIMEZONE = pytz.timezone('Australia/Sydney')
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
                print('changed', value)
        if changed:
            route.save()


def process_calendars(csvreader):
    result = defaultdict(list)
    for row in csvreader:
        values = {
            'start_date': datetime.strptime((row['start_date']), '%Y%m%d').date(),
            'end_date': datetime.strptime((row['end_date']), '%Y%m%d').date(),
        }
        for day in DAYS_OF_WEEK:
            values[day] = row[day] == '1'
        result[row['service_id']].append(row)
    return result


def process_trips(feed, calendars, trip_stops, csvreader):
    print('Processing trips')
    existing = {}
    for trip in Trip.objects.filter(route__feed=feed).order_by('version'):
        existing[trip.gtfs_trip_id] = trip

    routes = {}
    for route in Route.objects.filter(feed=feed):
        routes[route.gtfs_route_id] = route

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
                print('changed', value)
        if changed:
            trip.save()

        if gtfs_trip_id in trip_stops:
            to_create = []
            for tripstop_data in trip_stops[gtfs_trip_id]:
                to_create.append(TripStop(trip=trip, **tripstop_data))
            TripStop.objects.bulk_create(to_create)
        # trip_calendars = calendars[trip_row['service_id']]
        # TODO: enter the timetable days


def process_stops(feed, csvreader):
    print('Processing stops')
    existing = {}
    for stop in Stop.objects.filter(feed=feed):
        existing[stop.gtfs_stop_id] = stop

    for row in csvreader:
        gtfs_stop_id = row['stop_id']
        stop = existing.get(gtfs_stop_id, None)
        if stop is None:
            stop = Stop(feed=feed, gtfs_stop_id=gtfs_stop_id, name=row['stop_name'])
            stop.save()
        else:
            # Only update the stop if the name has changed
            if stop.name != row['stop_name']:
                stop.name = row['stop_name']
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


def fetch_timetable():
    feed = Feed.objects.get(slug='sydney-buses')
    if not TMP_FILE_PATH.is_file():
        headers = {'Authorization': 'apikey ' + GTFS_API_KEY}
        response = requests.get(GTFS_SCHEDULE_URL, headers=headers)
        print('Response received')
        if response.status_code == 200:
            with open(TMP_FILE_PATH, 'wb') as f:
                for chunk in response:
                    f.write(chunk)
    with zipfile.ZipFile(TMP_FILE_PATH) as zfile:
        process_agencies(feed, csv.DictReader(io.TextIOWrapper(zfile.open('agency.txt'))))
        process_routes(feed, csv.DictReader(io.TextIOWrapper(zfile.open('routes.txt'))))
        process_stops(feed, csv.DictReader(io.TextIOWrapper(zfile.open('stops.txt'))))
        calendars = process_calendars(csv.DictReader(io.TextIOWrapper(zfile.open('calendar.txt'))))
        trip_stops = process_stop_times(feed, csv.DictReader(io.TextIOWrapper(zfile.open('stop_times.txt'))))
        process_trips(feed, calendars, trip_stops, csv.DictReader(io.TextIOWrapper(zfile.open('trips.txt'))))

        return True
    return False

if __name__ == '__main__':
    success = fetch_timetable()
    print(success)
