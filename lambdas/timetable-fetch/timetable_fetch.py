from datetime import datetime
import os

import boto3
import psycopg2
import requests


S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'busshaming-timetable-dump')

GTFS_API_KEY = os.environ.get('TRANSPORT_NSW_API_KEY')
FEED_SLUG = 'nsw-buses'


DB_NAME = os.environ.get('DATABASE_NAME')
DB_HOST = os.environ.get('DATABASE_HOST')
DB_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DB_USER = os.environ.get('DATABASE_USER')
DB_PORT = os.environ.get('DATABASE_PORT', 5432)

FETCH_URLS = '''
SELECT ft.id, timetable_url, fetch_last_modified
FROM busshaming_feedtimetable ft
JOIN busshaming_feed f ON (f.id = ft.feed_id)
WHERE f.slug = %s
'''

UPDATE_LMT = '''
UPDATE busshaming_feedtimetable SET fetch_last_modified = %s
WHERE id = %s
'''


def upload_s3(filename, content):
    print(filename)
    print('Uploading to S3.')
    s3 = boto3.resource('s3')
    s3.Bucket(S3_BUCKET_NAME).put_object(Key=filename, Body=content)


def main(event, context):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    cur = conn.cursor()
    cur.execute(FETCH_URLS, (FEED_SLUG,))
    time = datetime.utcnow()
    headers = {'Authorization': 'apikey ' + GTFS_API_KEY}

    for tf_id, url, last_modified in cur.fetchall():
        print(f'Checking {url} ...')
        response = requests.head(url, headers=headers)
        if response.status_code == 200:
            lmt = response.headers['last-modified']
            if lmt != last_modified:
                print('Downloading...')
                response = requests.get(url, headers=headers)
                print('Fetching complete.')
                if response.status_code == 200:
                    filename = f'{FEED_SLUG}/{tf_id}/{time.isoformat()}.zip'
                    upload_s3(filename, response.content)
                    new_lmt = response.headers['last-modified']
                    cur.execute(UPDATE_LMT, (new_lmt, tf_id))
                    conn.commit()
                else:
                    print('Fetch failed:')
                    print(response.status_code)
                    print(response.content)
        else:
            print('Fetch failed:')
            print(response.status_code)
            print(response.content)
    conn.close()


if __name__ == '__main__':
    main(None, None)
