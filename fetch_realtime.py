import os
from datetime import datetime, timedelta


import pytz
import requests
from google.transit import gtfs_realtime_pb2

GTFS_API_KEY = os.environ.get('TRANSPORT_NSW_API_KEY')
GTFS_REALTIME_URL = 'https://api.transport.nsw.gov.au/v1/gtfs/realtime/buses/'
GTFS_VEHICLE_URL = 'https://api.transport.nsw.gov.au/v1/gtfs/vehiclepos/buses/'
FEED_TIMEZONE = pytz.timezone('Australia/Sydney')


def process_trip_update(trip_update, threshold):
    global count
    trip = trip_update.trip
    print(trip)
    for stop_update in trip_update.stop_time_update:
        if stop_update.arrival.time < threshold:
            print(trip.route_id)
            print(stop_update.stop_sequence)
            print(stop_update.arrival.delay)
            print(stop_update.arrival.time)
            print(threshold)
            print()


def fetch():
    feed = gtfs_realtime_pb2.FeedMessage()
    headers = {'Authorization': 'apikey ' + GTFS_API_KEY}
    response = requests.get(GTFS_REALTIME_URL, headers=headers)
    if response.status_code == 200:
        feed.ParseFromString(response.content)
        now = datetime.now(tz=FEED_TIMEZONE)
        threshold = int((now + timedelta(minutes=3)).timestamp())
        for entity in feed.entity:
            if entity.HasField('trip_update'):
                process_trip_update(entity.trip_update, threshold)
    else:
        print(response.status_code)
        print(response.content)


if __name__ == '__main__':
    fetch()
