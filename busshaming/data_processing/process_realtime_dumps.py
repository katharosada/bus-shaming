import os
from datetime import datetime, timedelta, timezone
import tempfile

from django.db import transaction

import boto3
import pytz
from google.transit import gtfs_realtime_pb2

from busshaming.models import Trip, TripDate, TripStop, RealtimeEntry, Route, Stop
from busshaming.enums import ScheduleRelationship

S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'busshaming-realtime-dumps')


DEBUG = False
global_stats = {}


SCHEDULE_RELATIONSHIP = dict(gtfs_realtime_pb2.TripDescriptor.ScheduleRelationship.items())

ROUTE_ID_SET = set()

upsert_log = {}

def to_schedule_relationship(proto):
    if proto == SCHEDULE_RELATIONSHIP['SCHEDULED']:
        return ScheduleRelationship.SCHEDULED.value
    elif proto == SCHEDULE_RELATIONSHIP['ADDED']:
        return ScheduleRelationship.ADDED.value
    elif proto == SCHEDULE_RELATIONSHIP['UNSCHEDULED']:
        return ScheduleRelationship.UNSCHEDULED.value
    elif proto == SCHEDULE_RELATIONSHIP['CANCELED']:
        return ScheduleRelationship.CANCELLED.value
    return ScheduleRelationship.SCHEDULED.value


def add_missing_tripdate(feed, realtime_trip, vehicle_id):
    gtfs_trip_id = realtime_trip.trip_id
    start_date = realtime_trip.start_date
    if DEBUG:
        print(f'Adding missing trip date for gtfs id {gtfs_trip_id} on date {start_date}')
    date = datetime.strptime(start_date, '%Y%m%d').date()

    if not realtime_trip.route_id:
        return None

    with transaction.atomic():
        try:
            trip = Trip.objects.filter(gtfs_trip_id=gtfs_trip_id, route__gtfs_route_id=realtime_trip.route_id).order_by('-version').first()
        except Trip.DoesNotExist as e:
            trip = None
        if trip is None:
            trip = add_missing_trip(feed, realtime_trip)
        if trip is None:
            return None
    if DEBUG:
        print(f'Found trip: {trip}')
    try:
        return TripDate.objects.get(trip=trip, date=date)
    except TripDate.DoesNotExist as e:
        pass
    schedule_relationship = to_schedule_relationship(realtime_trip.schedule_relationship)    
    tripdate = TripDate(trip=trip, date=date, added_from_realtime=True, vehicle_id=vehicle_id, schedule_relationship=schedule_relationship)
    tripdate.save()
    if trip.scheduled:
        global_stats['missing_tripdates'] += 1
    else:
        global_stats['unscheduled_tripdates'] += 1
    if not trip.added_from_realtime:
        global_stats['missing_tripdates_but_trip_existed'] += 1
        print(f'Trip {trip} was in the timetable, just not for tripdate {tripdate}')
    return tripdate


def add_missing_trip(feed, realtime_trip):
    gtfs_trip_id = realtime_trip.trip_id
    if realtime_trip.route_id not in ROUTE_ID_SET:
        return None
    if realtime_trip.schedule_relationship == SCHEDULE_RELATIONSHIP['ADDED'] and '_' in gtfs_trip_id:
        original_trip_id = gtfs_trip_id.split('_')[0]
        trip = Trip.objects.filter(gtfs_trip_id=original_trip_id).order_by('-version').first()
        if trip is not None:
            global_stats['unscheduled_trips'] += 1
            new_trip = trip.clone_to_unscheduled(gtfs_trip_id)
            return new_trip
    try:
        route = Route.objects.get(feed=feed, gtfs_route_id=realtime_trip.route_id)
    except Route.DoesNotExist as e2:
        global_stats['missing_routes'] += 1
        print(f'Route did not exist: {realtime_trip.route_id}')
        return None
    print(f'Trip with gtfs id {gtfs_trip_id} (from route {route}) does not exist!!')
    newtrip = Trip(
        gtfs_trip_id=gtfs_trip_id,
        active=True,
        direction=0,
        route=route,
        added_from_realtime=True,
        wheelchair_accessible=False,
        bikes_allowed=False,
        scheduled=(realtime_trip.schedule_relationship == SCHEDULE_RELATIONSHIP['SCHEDULED'])
    )
    newtrip.save()
    global_stats['missing_trips'] += 1
    if DEBUG:
        print(f'Added new trip: {newtrip}')
    return newtrip


def format_stop_time(time, plus_24h):
    hour = time.hour
    if plus_24h:
        hour += 24
    return f'{hour:02d}:{time.minute:02d}:{time.second:02d}'


def get_stop(feed, stop_id, stops):
    with transaction.atomic():
        try:
            stop = Stop.objects.get(feed=feed, gtfs_stop_id=stop_id)
        except Stop.DoesNotExist:
            stop = Stop(feed=feed, gtfs_stop_id=stop_id, name='Unknown', position=None)
            stop.save()
            stops[stop.gtfs_stop_id] = stop
            global_stats['missing_stops'] += 1
    return stop


def process_trip_update(feed, trip_dates, stops, feed_tz, trip_update, threshold, start_date_str, start_date_str_after_midnight):
    global_stats['trip_updates_found'] += 1
    trip = trip_update.trip
    plus_24h = False
    if trip.start_time < '04:00:00':
        if trip.start_date == start_date_str_after_midnight:
            trip.start_date = start_date_str
            plus_24h = True
        else:
            return
    if trip.start_date != start_date_str:
        return
    # Some trips are missing ids altogether.
    # Construct an id from 'unscheduled' and the vehicle id
    if not trip.trip_id:
        if not trip_update.vehicle.id:
            return
        global_stats['missing_trip_id'] += 1
        trip.trip_id = 'unscheduled_' + trip_update.vehicle.id
    key = (trip.trip_id, start_date_str)
    if key not in trip_dates:
        trip_date = add_missing_tripdate(feed, trip, trip_update.vehicle.id)
        if trip_date is not None:
            if DEBUG:
                print("COULDN'T FIND IN SCHEDULE: {}".format(key))
                print(trip)
            trip_dates[key] = trip_date
    else:
        trip_date = trip_dates[key]
    if trip_date is None:
        return
    if trip.schedule_relationship != SCHEDULE_RELATIONSHIP['SCHEDULED']:
        trip_date.schedule_relationship = to_schedule_relationship(trip.schedule_relationship)
        trip_date.vehicle_id = trip_update.vehicle.id
        trip_date.save()
    if DEBUG:
        print(f'Upserting realtime entries for tripdate {trip_date.id}')
    for stop_update in trip_update.stop_time_update:
        global_stats['stop_updates_found'] += 1
        if stop_update.arrival.time < threshold:
            if stop_update.stop_id in stops:
                stop = stops[stop_update.stop_id]
            else:
                stop = get_stop(feed, stop_update.stop_id, stops)
            arrival_time = datetime.fromtimestamp(stop_update.arrival.time, feed_tz)
            departure_time = datetime.fromtimestamp(stop_update.departure.time, feed_tz)
            schedule_relationship = to_schedule_relationship(stop_update.schedule_relationship)
            # Upsert RealtimeEntry
            # RealtimeEntry.objects.upsert(trip_date.id, stop.id, stop_update.stop_sequence, arrival_time, stop_update.arrival.delay, departure_time, stop_update.departure.delay)
            upsert_log[(trip_date.id, stop.id, stop_update.stop_sequence)] = (arrival_time, stop_update.arrival.delay, departure_time, stop_update.departure.delay, schedule_relationship)
            global_stats['stop_updates_stored'] += 1


def process_dump_contents(feed, contents, trip_dates, stops, fetchtime, feed_tz, start_date_str, start_date_str_after_midnight):
    global global_stats
    global_stats = {
        'trip_updates_found': 0,
        'stop_updates_found': 0,
        'stop_updates_stored': 0,
        'missing_trips': 0,
        'unscheduled_trips': 0,
        'unscheduled_tripdates': 0,
        'missing_stops': 0,
        'missing_trip_id': 0,
        'missing_tripdates': 0,
        'missing_tripdates_but_trip_existed': 0,
        'missing_routes': 0,
    }
    feed_message = gtfs_realtime_pb2.FeedMessage()
    feed_message.ParseFromString(contents)
    threshold = int((fetchtime + timedelta(minutes=5)).timestamp())
    for entity in feed_message.entity:
        if entity.HasField('trip_update'):
            process_trip_update(feed, trip_dates, stops, feed_tz, entity.trip_update, threshold, start_date_str, start_date_str_after_midnight)
    for stat in global_stats:
        print(f'{stat}: {global_stats[stat]}')


def fetch_next_dumps(realtime_progress, num_dumps, temp_dir):
    print(f'Processing next {num_dumps} realtime dumps in {realtime_progress}')
    client = boto3.client('s3')
    file_prefix = f'{realtime_progress.feed.slug}/'

    last_processed_file = realtime_progress.last_processed_dump
    if last_processed_file is None:
        last_processed_file = file_prefix + realtime_progress.start_time().strftime('%Y-%m-%dT%H:%M:%S.%f')

    if last_processed_file is not None:
        response = client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=file_prefix, StartAfter=last_processed_file, MaxKeys=num_dumps)
    else:
        response = client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=file_prefix, MaxKeys=num_dumps)

    results = []

    if response['KeyCount'] != 0:
        for content in response['Contents']:
            key = content['Key']
            s3 = boto3.resource('s3')
            tmp_path = os.path.join(temp_dir, key.split('/')[1])
            if DEBUG:
                print(f'Fetching {key}...')
            s3.Object(S3_BUCKET_NAME, key).download_file(tmp_path)
            results.append((key, tmp_path))
    else:
        print(f'No new realtime dump data for {feed}')
    return results


def refresh_route_list():
    global ROUTE_LIST
    ROUTE_ID_SET = set(Route.objects.values_list('gtfs_route_id', flat=True))

def clear_upsert_log():
    global upsert_log
    upsert_log = {}

def write_upsert_log():
    global upsert_log
    print(f'Upsert log contains {len(upsert_log)} entries.')
    list_batch = []
    for realtime_key, value in upsert_log.items():
        #RealtimeEntry.objects.upsert(trip_date.id, stop.id, stop_update.stop_sequence, arrival_time, stop_update.arrival.delay, departure_time, stop_update.departure.delay)
        list_batch.append((*realtime_key, *value))
    start = 0
    while start < len(list_batch):
        batch = list_batch[start : start + 20]
        start += 20
        RealtimeEntry.objects.upsert_bulk(batch)


def process_next(realtime_progress, num_dumps):
    feed = realtime_progress.feed
    succeed = realtime_progress.take_processing_lock()
    clear_upsert_log()
    if not succeed:
        # It'll try again with another progress
        return
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            cached_dumps = fetch_next_dumps(realtime_progress, num_dumps, temp_dir)
            feed_tz = pytz.timezone(feed.timezone)
            start_date_str = realtime_progress.start_date.strftime('%Y%m%d')
            start_date_str_after_midnight = (realtime_progress.start_date + timedelta(days=1)).strftime('%Y%m%d')

            if len(cached_dumps) != 0:
                # Prefetch stops
                stops = {}
                for stop in Stop.objects.filter(feed=feed):
                    stops[stop.gtfs_stop_id] = stop

                # Prefetch Routes
                refresh_route_list()

                # Prefetch Trip Dates
                first_key = cached_dumps[0][0]
                trip_dates = {}
                datestr = os.path.split(first_key)[1].rstrip('.pb')
                fetchtime = datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S.%f').replace(tzinfo=timezone.utc)
                # Assume no bus runs longer than 48h
                fetchtime = fetchtime.astimezone(feed_tz)
                for trip_date in TripDate.objects.filter(date=realtime_progress.start_date).prefetch_related('trip'):
                    datestr = trip_date.date.strftime('%Y%m%d')
                    trip_dates[(trip_date.trip.gtfs_trip_id, datestr)] = trip_date

                for key, tmp_file in cached_dumps:
                    datestr = os.path.split(key)[1].rstrip('.pb')
                    fetchtime = datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S.%f').replace(tzinfo=timezone.utc)
                    # Assume no bus runs longer than 48h
                    fetchtime = fetchtime.astimezone(feed_tz)
                    with open(tmp_file, 'rb') as f:
                        contents = f.read()
                        print(f'Processing {key}')
                        process_dump_contents(feed, contents, trip_dates, stops, fetchtime, feed_tz, start_date_str, start_date_str_after_midnight)
                    if fetchtime > realtime_progress.end_time():
                        break
        # Update where we're up to.
        write_upsert_log()
        if fetchtime > realtime_progress.end_time():
            realtime_progress.update_progress(key, True)
        else:
            realtime_progress.update_progress(key, False)
    finally:
        realtime_progress.release_processing_lock()
