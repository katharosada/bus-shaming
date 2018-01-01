import os
from datetime import datetime, timedelta, timezone
import tempfile

import boto3
import pytz
from google.transit import gtfs_realtime_pb2

from busshaming.models import Feed, Trip, TripDate, RealtimeEntry, Stop

S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'busshaming-realtime-dumps')


def add_missing_tripdate(gtfs_trip_id, start_date):
    print(f'Adding missing trip date for gtfs id {gtfs_trip_id} on date {start_date}')
    date = datetime.strptime(start_date, '%Y%m%d').date()
    try:
        trip = Trip.objects.get(gtfs_trip_id=gtfs_trip_id)
        print(f'Found trip: {trip}')
        assert TripDate.objects.filter(trip=trip, date=date).count() == 0
        tripdate = TripDate(trip=trip, date=date, added_from_realtime=True)
        tripdate.save()
        return tripdate
    except Trip.DoesNotExist as e:
        print(f'Trip with gtfs id {gtfs_trip_id} does not exist!!')
        return None


def process_trip_update(trip_dates, stops, feed_tz, trip_update, threshold):
    trip = trip_update.trip
    key = (trip.trip_id, trip.start_date)
    if key not in trip_dates:
        print(trip)
        print("CAN'T FIND IN SCHEDULE: {}".format(key))
        trip_date = add_missing_tripdate(trip.trip_id, trip.start_date)
    else:
        trip_date = trip_dates[key]
    print(f'Upserting realtime entries for tripdate {trip_date.id}')
    for stop_update in trip_update.stop_time_update:
        if stop_update.arrival.time < threshold:
            stop = stops[stop_update.stop_id]
            arrival_time = datetime.fromtimestamp(stop_update.arrival.time, feed_tz)
            departure_time = datetime.fromtimestamp(stop_update.departure.time, feed_tz)
            # Upsert RealtimeEntry
            RealtimeEntry.objects.upsert(trip_date.id, stop.id, stop_update.stop_sequence, arrival_time, stop_update.arrival.delay, departure_time, stop_update.departure.delay)


def process_dump_contents(contents, trip_dates, stops, feed_tz):
    feed_message = gtfs_realtime_pb2.FeedMessage()
    feed_message.ParseFromString(contents)
    now = datetime.now(tz=feed_tz)
    threshold = int((now + timedelta(minutes=3)).timestamp())
    for entity in feed_message.entity:
        if entity.HasField('trip_update'):
            process_trip_update(trip_dates, stops, feed_tz, entity.trip_update, threshold)


def fetch_next_dumps(feed, num_dumps):
    print(f'Processing next {num_dumps} realtime dumps')
    client = boto3.client('s3')
    file_prefix = f'{feed.slug}/'
    last_processed_file = feed.last_processed_dump

    if last_processed_file is not None:
        response = client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=file_prefix, StartAfter=last_processed_file)
    else:
        response = client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=file_prefix)

    results = []

    if response['KeyCount'] != 0:
        print(f'{response["KeyCount"]} new realtime dump(s) for {feed}')
        for i in range(num_dumps):
            key = response['Contents'][i]['Key']
            s3 = boto3.resource('s3')
            tmp, tmp_path = tempfile.mkstemp()
            print(f'Fetching {key}...')
            s3.Object(S3_BUCKET_NAME, key).download_file(tmp_path)
            results.append((key, tmp_path))
    else:
        print(f'No new realtime dump data for {feed}')
    return results


def process_next(num_dumps):
    feed = Feed.objects.get(slug='nsw-buses')
    cached_dumps = fetch_next_dumps(feed, num_dumps)
    feed_tz = pytz.timezone(feed.timezone)

    if len(cached_dumps) != 0:
        stops = {}
        for stop in Stop.objects.filter(feed=feed):
            stops[stop.gtfs_stop_id] = stop

        for key, tmp_file in cached_dumps:
            trip_dates = {}
            datestr = os.path.split(key)[1].rstrip('.pb')
            fetchtime = datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S.%f').replace(tzinfo=timezone.utc)
            # Assume no bus runs longer than 48h
            fetchtime = fetchtime.astimezone(feed_tz)
            start = (fetchtime - timedelta(days=2)).date()
            end = (fetchtime + timedelta(days=2)).date()
            for trip_date in TripDate.objects.filter(date__gte=start, date__lte=end).prefetch_related('trip'):
                datestr = trip_date.date.strftime('%Y%m%d')
                trip_dates[(trip_date.trip.gtfs_trip_id, datestr)] = trip_date
            with open(tmp_file, 'rb') as f:
                contents = f.read()
                process_dump_contents(contents, trip_dates, stops, feed_tz)
