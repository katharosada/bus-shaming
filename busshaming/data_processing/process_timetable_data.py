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
        print(f'Downloading file: {key}')
        s3 = boto3.resource('s3')
        tmp_path = os.path.join(temp_dir, key.split('/')[-1])
        s3.Object(S3_BUCKET_NAME, key).download_file(tmp_path)
        return tmp_path, key
    print(f'No new timetable data for {timetable_feed}')
    return None, None


def fill_tripdate_gap(feed, timetable_feed, until_time, temp_dir):
    if not timetable_feed.last_processed_zip:
        return
    if not timetable_feed.processed_watermark:
        timetable_feed.processed_watermark = datetime_from_s3_key(timetable_feed.last_processed_zip) + timedelta(days=13)
    # If it's been a long time since the last timetable, we need to update the trip dates
    # since we only fill them 2 weeks in advance
    if timetable_feed.processed_watermark < until_time:
        s3 = boto3.resource('s3')
        tmp_path = os.path.join(temp_dir, timetable_feed.last_processed_zip.split('/')[-1])
        s3.Object(S3_BUCKET_NAME, timetable_feed.last_processed_zip).download_file(tmp_path)
        
    while timetable_feed.processed_watermark < until_time:
        new_fetchtime = timetable_feed.processed_watermark
        print(f'Updating tripdate gap from time: {new_fetchtime} using file {timetable_feed.last_processed_zip}')
        success, limit = process_zip(feed, tmp_path, new_fetchtime)
        if success:
            timetable_feed.processed_watermark = limit
            timetable_feed.save()
        new_fetchtime = limit
        print(f'Updated up to {limit} now.')


def datetime_from_s3_key(obj_key):
    datestr = os.path.split(obj_key)[1].rstrip('.zip')
    fetchtime = datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%S.%f').replace(tzinfo=timezone.utc)
    return fetchtime


def fetch_and_process_timetables():
    feed = Feed.objects.get(slug='nsw-buses')
    timetable_feeds = FeedTimetable.objects.filter(feed=feed, active=True).order_by('id').prefetch_related('feed')
    for timetable_feed in timetable_feeds:
        print(f'Looking at {timetable_feed}')
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path, obj_key = download_zip(timetable_feed, temp_dir)
            if tmp_path is not None:
                # Fill potential trip date gap:
                fill_tripdate_gap(feed, timetable_feed, datetime_from_s3_key(obj_key), temp_dir)
                # Get datetime from filename
                fetchtime = datetime_from_s3_key(obj_key)
                success, limit = process_zip(feed, tmp_path, fetchtime)
                if success:
                    timetable_feed.processed_watermark = limit
                    timetable_feed.last_processed_zip = obj_key
                    timetable_feed.save()
                os.remove(tmp_path)
            else:
                # If there's no updates, we need to make sure we keep filling out the tripdates
                # We need the timetable to be filled out up to 7 days from now.
                last_week = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(days=7)
                fill_tripdate_gap(feed, timetable_feed, datetime.utcnow().replace(tzinfo=timezone.utc), temp_dir)


def process_zip(feed, tmp_path, fetchtime):
    with zipfile.ZipFile(tmp_path) as zfile:
        return upsert_timetable_data.process_zip(feed, zfile, fetchtime)
    return False, None
