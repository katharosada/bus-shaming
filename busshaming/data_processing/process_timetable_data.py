import os
import tempfile
import zipfile

import boto3
import pytz

from busshaming.models import Feed, FeedTimetable
from busshaming.data_processing import upsert_timetable_data


S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'busshaming-timetable-dumps')
FEED_TIMEZONE = pytz.timezone('Australia/Sydney')


def download_zip(timetable_feed):
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
        tmp, tmp_path = tempfile.mkstemp()
        s3.Object(S3_BUCKET_NAME, key).download_file(tmp_path)
        return tmp_path, key
    print(f'No new timetable data for {timetable_feed}')
    return None, None


def fetch_and_process_timetables():
    feed = Feed.objects.get(slug='nsw-buses')
    timetable_feeds = FeedTimetable.objects.filter(feed=feed).prefetch_related('feed')
    for timetable_feed in timetable_feeds:
        tmp_path, obj_key = download_zip(timetable_feed)
        if tmp_path is not None:
            success = process_zip(feed, tmp_path)
            if success:
                timetable_feed.last_processed_zip = obj_key
                timetable_feed.save()
            os.remove(tmp_path)


def process_zip(feed, tmp_path):
    with zipfile.ZipFile(tmp_path) as zfile:
        return upsert_timetable_data.process_zip(feed, zfile)
    return False
