import django
django.setup()

from datetime import datetime
import hashlib
import os
import io
import sys
import csv
import tempfile
import zipfile

from collections import defaultdict


from busshaming.models import Feed, FeedTimetable, Trip, TripStop, Stop, StopSequence
from busshaming.data_processing import process_timetable_data


def backfill_timepoints(stops, tmp_path):
    gtfs_ids = set(Trip.objects.filter(stop_sequence__has_timepoints=False).values_list('gtfs_trip_id', flat=True))
    stop_sets = defaultdict(list)
    with zipfile.ZipFile(tmp_path) as zfile:
        csvreader = csv.DictReader(io.TextIOWrapper(zfile.open('stop_times.txt')))
        for row in csvreader:
            gtfs_trip_id = row['trip_id']
            if gtfs_trip_id not in gtfs_ids:
                continue
            new_stop = {
                'stop': stops[row['stop_id']],
                'sequence': int(row['stop_sequence']),
                'timepoint': row['timepoint'] == '1'
            }
            stop_sets[gtfs_trip_id].append(new_stop)

    for gtfs_trip_id in stop_sets:
        if gtfs_trip_id not in gtfs_ids:
            continue
        stop_set = stop_sets[gtfs_trip_id]
        stop_set.sort(key=lambda s: s['sequence'])
        sequence_hash = hash_stop_sequence([s['stop'].id for s in stop_set])
        relevant_trips = list(Trip.objects.filter(stop_sequence__sequence_hash=sequence_hash).all())
        route_id = None
        for trip in relevant_trips:
            if trip.gtfs_trip_id == gtfs_trip_id:
                route_id = trip.route_id
                break
        relevant_trips = [t for t in relevant_trips if t.route_id == route_id]
        relevant_trip_ids = [t.id for t in relevant_trips]
        relevant_gtfs_trip_ids = [t.gtfs_trip_id for t in relevant_trips]

        timepoint_stops = [s['stop'].id for s in stop_set if s['timepoint']]
        timepoint_sequences = [s['sequence'] for s in stop_set if s['timepoint']]
        tripstops_query = TripStop.objects.filter(trip_id__in=relevant_trip_ids, stop_id__in=timepoint_stops, sequence__in=timepoint_sequences)
        tripstops = tripstops_query.count()
        if not (len(timepoint_stops) * len(relevant_trip_ids) == tripstops):
            print(f'{gtfs_trip_id}: {len(timepoint_stops)} timepoints out of {len(stop_set)}')
            print(f'{route_id}')
            print(f'assert {len(timepoint_stops)} * {len(relevant_trip_ids)} == {tripstops}')
            return False
        tripstops = tripstops_query.update(timepoint=True)
        StopSequence.objects.filter(sequence_hash=sequence_hash, route_id=route_id).update(has_timepoints=True)
        gtfs_ids.difference_update(relevant_gtfs_trip_ids)
    return True


def hash_stop_sequence(stopid_sequence):
    # TODO: Refactor this to StopSequence as a static function
    key = ','.join(str(stop_id) for stop_id in stopid_sequence)
    keyhash = hashlib.sha256(key.encode('ascii')).hexdigest()
    return keyhash


def filename_from_date(id, date):
    datestr = date.strftime('%Y-%m-%dT%H:%M:%S.%f')
    return f'nsw-buses/{id}/{datestr}.zip'


def date_from_filename(filename):
    datestr = os.path.split(filename)[1].rstrip('.zip')
    fetchtime = datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S.%f')
    return fetchtime


def main(date):
    feed = Feed.objects.get(slug='nsw-buses')
    timetable_feeds = {}
    for tf in FeedTimetable.objects.filter(feed=feed).order_by('id').prefetch_related('feed'):
        timetable_feeds[tf.id] = tf

    feed_dates = {}
    for tfid in timetable_feeds:
        feed_dates[tfid] = filename_from_date(tfid, date)

    # Prefetch all stops:
    stops = {}
    for stop in Stop.objects.filter(feed=feed):
        stops[stop.gtfs_stop_id] = stop

    halt = False
    while len(feed_dates) != 0 and not halt:
        # Get the minimum feed date
        timetable_feed_id = min(feed_dates, key=lambda tfid: date_from_filename(feed_dates[tfid]))
        timetable_feed = timetable_feeds[timetable_feed_id]

        filename = feed_dates[timetable_feed_id]
        print('Min date:', filename)
        with tempfile.TemporaryDirectory() as temp_dir:
            timetable_feed.last_processed_zip = filename
            tmp_path, obj_key = process_timetable_data.download_zip(timetable_feed, temp_dir)
            if tmp_path is None:
                del feed_dates[timetable_feed_id]
                break
            print(f'Processing {obj_key}')
            success = backfill_timepoints(stops, tmp_path)
            if not success:
                halt = True

            print('Finished:', obj_key)
            feed_dates[timetable_feed_id] = obj_key


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <starting date>')
        sys.exit(1)

    date = datetime.strptime(sys.argv[1], '%Y-%m-%d')
    main(date)
