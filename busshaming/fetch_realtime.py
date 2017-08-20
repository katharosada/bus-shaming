import os
from datetime import datetime, timedelta

import django
import pytz
import requests
from google.transit import gtfs_realtime_pb2

django.setup()

from busshaming.models import Feed, TripDate, RealtimeEntry, Stop

GTFS_API_KEY = os.environ.get('TRANSPORT_NSW_API_KEY')


def process_trip_update(trip_dates, stops, feed_tz, trip_update, threshold):
    trip = trip_update.trip
    key = (trip.trip_id, trip.start_date)
    # trip_date = trip_dates[key]
    if key not in trip_dates:
        print(trip)
        print("CAN'T FIND IN SCHEDULE: {}".format(key))
        return
    trip_date = trip_dates[key]
    for stop_update in trip_update.stop_time_update:
        if stop_update.arrival.time < threshold:
            stop = stops[stop_update.stop_id]
            arrival_time = datetime.fromtimestamp(stop_update.arrival.time, feed_tz)
            departure_time = datetime.fromtimestamp(stop_update.departure.time, feed_tz)
            # Upsert RealtimeEntry
            RealtimeEntry.objects.upsert(trip_date.trip_id, stop.id, stop_update.stop_sequence, arrival_time, stop_update.arrival.delay, departure_time, stop_update.departure.delay)


def fetch():
    feed = Feed.objects.get(slug='nsw-buses')
    feed_tz = pytz.timezone(feed.timezone)
    stops = {}
    for stop in Stop.objects.filter(feed=feed):
        stops[stop.gtfs_stop_id] = stop
    trip_dates = {}
    today = datetime.now(tz=feed_tz).date()
    yesterday = today - timedelta(days=1)
    for trip_date in TripDate.objects.filter(date__gte=yesterday, date__lte=today).prefetch_related('trip'):
        datestr = trip_date.date.strftime('%Y%m%d')
        trip_dates[(trip_date.trip.gtfs_trip_id, datestr)] = trip_date

    feed_message = gtfs_realtime_pb2.FeedMessage()
    headers = {'Authorization': 'apikey ' + GTFS_API_KEY}
    print('fetching...')
    response = requests.get(feed.realtime_feed_url, headers=headers)
    print('fetching complete.')
    if response.status_code == 200:
        feed_message.ParseFromString(response.content)
        now = datetime.now(tz=feed_tz)
        threshold = int((now + timedelta(minutes=3)).timestamp())
        for entity in feed_message.entity:
            if entity.HasField('trip_update'):
                process_trip_update(trip_dates, stops, feed_tz, entity.trip_update, threshold)
    else:
        print(response.status_code)
        print(response.content)


if __name__ == '__main__':
    fetch()
