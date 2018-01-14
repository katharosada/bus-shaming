import os
import tempfile
import zipfile
from datetime import datetime, timedelta, timezone

import boto3
import pytz

from busshaming.models import Feed, FeedTimetable
from busshaming.data_processing import upsert_timetable_data


S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'busshaming-timetable-dumps')
FEED_TIMEZONE = pytz.timezone('Australia/Sydney')


def download_zip(timetable_feed, temp_dir):
    client = boto3.client('s3')
    file_prefix = f'{timetable_feed.feed.slug}/{timetable_feed.id}/'
    last_processed_file = timetable_feed.last_processed_zip

    if last_processed_file is not None:
        response = client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=file_prefix, StartAfter=last_processed_file)
    else:
        response = client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=file_prefix)
    if response['KeyCount'] != 0:
        print(f'{response["KeyCount"]} new timetable data for {timetable_feed}')
        key = response['Contents'][0]['Key']
        s3 = boto3.resource('s3')
        tmp_path = os.path.join(temp_dir, key.split('/')[-1])
        s3.Object(S3_BUCKET_NAME, key).download_file(tmp_path)
        return tmp_path, key
    print(f'No new timetable data for {timetable_feed}')
    return None, None


def fill_tripdate_gap(feed, last_processed_file, new_file, temp_dir):
    # If it's been almost 2 weeks from the last timetable, we need to update the trip dates
    # since we only fill them 2 weeks in advance
    new_fetchtime = datetime_from_s3_key(last_processed_file) + timedelta(days=13)
    while new_fetchtime < datetime_from_s3_key(new_file):
        s3 = boto3.resource('s3')
        tmp_path = os.path.join(temp_dir, key.split('/')[-1])
        s3.Object(S3_BUCKET_NAME, last_processed_file).download_file(tmp_path)
        print(f'Updating tripdate gap to time: {new_fetchtime}')
        process_zip(feed, tmp_path, new_fetchtime)
        new_fetchtime += timedelta(days=13)


def datetime_from_s3_key(obj_key):
    datestr = os.path.split(obj_key)[1].rstrip('.zip')
    fetchtime = datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S.%f').replace(tzinfo=timezone.utc)
    return fetchtime


def fetch_and_process_timetables():
    feed = Feed.objects.get(slug='nsw-buses')
    timetable_feeds = FeedTimetable.objects.filter(feed=feed).order_by('id').prefetch_related('feed')
    for timetable_feed in timetable_feeds:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path, obj_key = download_zip(timetable_feed, temp_dir)
            if tmp_path is not None:
                # Fill potential trip date gap:
                if timetable_feed.last_processed_zip:
                    fill_tripdate_gap(feed, timetable_feed.last_processed_zip, obj_key, temp_dir)
                # Get datetime from filename
                fetchtime = datetime_from_s3_key(obj_key)
                success = process_zip(feed, tmp_path, fetchtime)
                if success:
                    timetable_feed.last_processed_zip = obj_key
                    timetable_feed.save()
                os.remove(tmp_path)


def process_zip(feed, tmp_path, fetchtime):
    with zipfile.ZipFile(tmp_path) as zfile:
        return upsert_timetable_data.process_zip(feed, zfile, fetchtime)
    return False
