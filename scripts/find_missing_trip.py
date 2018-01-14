from datetime import datetime, timedelta
import os
import io
import sys
import csv
import zipfile

import django

django.setup()

from busshaming.models import Feed, FeedTimetable
from busshaming.data_processing import process_timetable_data


def search_zip(gtfs_trip_id, zip_path):
    print('Searching for', gtfs_trip_id, zip_path)
    with zipfile.ZipFile(tmp_path) as zfile:
        csvreader = csv.DictReader(io.TextIOWrapper(zfile.open('trips.txt')))
        for trip_row in csvreader:
            #print(trip_row)
            #print(trip_row['trip_id'])
            if gtfs_trip_id == trip_row['trip_id']:
                print("OMG FOUND")
                return True
    return False

def show_relevant_details(gtfs_trip_id, zip_path):
    with zipfile.ZipFile(tmp_path) as zfile:
        print('trips.txt')
        csvreader = csv.DictReader(io.TextIOWrapper(zfile.open('trips.txt')))
        for row in csvreader:
            if gtfs_trip_id == row['trip_id']:
                print(row)
                service_id = row['service_id']
        print('stop_times.txt')
        csvreader = csv.DictReader(io.TextIOWrapper(zfile.open('stop_times.txt')))
        for row in csvreader:
            if gtfs_trip_id == row['trip_id']:
                print(row)
        print('calendar_dates.txt')
        csvreader = csv.DictReader(io.TextIOWrapper(zfile.open('calendar_dates.txt')))
        for row in csvreader:
            if service_id == row['service_id']:
                print(row)
        print('calendar.txt')
        csvreader = csv.DictReader(io.TextIOWrapper(zfile.open('calendar.txt')))
        for row in csvreader:
            if service_id == row['service_id']:
                print(row)

    return False


def filename_from_date(id, date):
    datestr = date.strftime('%Y-%m-%dT%H:%M:%S.%f')
    return f'nsw-buses/{id}/{datestr}.zip'


def date_from_filename(filename):
    datestr = os.path.split(filename)[1].rstrip('.zip')
    fetchtime = datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S.%f')
    return fetchtime


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f'Usage: {sys.argv[0]} <gtfs_trip_id> <expected_date e.g. 2017-08-21>')
        sys.exit(1)

    gtfs_trip_id = sys.argv[1]
    date = datetime.strptime(sys.argv[2], '%Y-%m-%d')

    feed = Feed.objects.get(slug='nsw-buses')
    timetable_feeds = FeedTimetable.objects.filter(feed=feed).order_by('id').prefetch_related('feed')
    found = False
    for timetable_feed in timetable_feeds:
        filename = filename_from_date(timetable_feed.id, date - timedelta(days=14))

        while filename == '' or date_from_filename(filename) <= date:
            timetable_feed.last_processed_zip = filename
            print(filename)
            tmp_path, obj_key = process_timetable_data.download_zip(timetable_feed)
            if tmp_path is None:
                break

            filename = obj_key
            print(obj_key)

            found = search_zip(gtfs_trip_id, tmp_path)
            if found:
                show_relevant_details(gtfs_trip_id, tmp_path)
                break

        if found:
            break
