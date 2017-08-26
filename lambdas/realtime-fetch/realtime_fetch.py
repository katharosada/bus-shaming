from datetime import datetime
import os

import boto3
import requests


GTFS_API_KEY = os.environ.get('TRANSPORT_NSW_API_KEY')
REALTIME_URL = 'https://api.transport.nsw.gov.au/v1/gtfs/realtime/buses/'
FEED_SLUG = 'nsw-buses'


def upload_s3(filename, content):
    print('Uploading to S3.')
    s3 = boto3.resource('s3')
    s3.Bucket('busshaming-realtime-dumps').put_object(Key=filename, Body=content)


def main(event, context):
    time = datetime.utcnow()
    headers = {'Authorization': 'apikey ' + GTFS_API_KEY}
    print('fetching...')
    response = requests.get(REALTIME_URL, headers=headers)
    print('fetching complete.')
    if response.status_code == 200:
        filename = f'{FEED_SLUG}/{time.isoformat()}.pb'
        upload_s3(filename, response.content)
    else:
        print('Fetch failed:')
        print(response.status_code)
        print(response.content)
