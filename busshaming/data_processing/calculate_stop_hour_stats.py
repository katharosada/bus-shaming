from datetime import datetime, timedelta
from statistics import mean, median
from collections import defaultdict

import pytz

from busshaming.enums import ScheduleRelationship
from busshaming.models import TripStop, RealtimeEntry, RouteStopDay, RouteStopHour

AU_TIMEZONE = pytz.timezone('Australia/Sydney')

meta_stats = {}


def get_datetime_from_36h_string(date, timestr):
    hour, minute, second = [int(s) for s in timestr.split(':')]
    if hour >= 24:
        hour -= 24
        date = date + timedelta(days=1)
    return AU_TIMEZONE.localize(datetime(date.year, date.month, date.day, hour, minute))


def calculated_weighted_gaps(day_start, arrival_times):
    weighted_gaps = [[] for i in range(28)] # [[(gap, weight], ...], ...]
    prev_arrival_time = day_start
    prev_delta = 0
    for arrival_time in arrival_times:
        while prev_arrival_time < arrival_time:
            cur_delta = int((arrival_time - day_start).total_seconds() // 3600)
            gap = arrival_time - prev_arrival_time
            if prev_delta < cur_delta:
                end_of_prev_delta = day_start + timedelta(hours=prev_delta + 1)
                avg_wait = (gap + (arrival_time - end_of_prev_delta)) / 2
                weight = end_of_prev_delta - prev_arrival_time
                weighted_gaps[prev_delta].append((avg_wait.total_seconds(), weight.total_seconds()))
                prev_delta = prev_delta + 1
                prev_arrival_time = end_of_prev_delta
            else:
                weighted_gaps[cur_delta].append((gap.total_seconds() / 2, gap.total_seconds()))
                prev_delta = cur_delta
                prev_arrival_time = arrival_time
    return weighted_gaps

def expected_wait(weighted_gaps):
    return sum(gap * weight for gap, weight in weighted_gaps) / sum(weight for gap, weight in weighted_gaps)

def is_incomplete_day(weighted_gaps):
    return len(weighted_gaps) == 0 or sum(weight for gap, weight in weighted_gaps) < 3600


def calculate_stops(date, route_id, trip_dates):
    trip_date_ids = [trip_date.id for trip_date in trip_dates]
    trip_ids = [trip_date.trip_id for trip_date in trip_dates if trip_date.trip.scheduled]

    final_route_stop_day_list = []
    final_route_stop_hour_list = []

    all_realtimes = RealtimeEntry.objects.filter(trip_date_id__in=trip_date_ids).all()
    realtimes_by_stop = defaultdict(list)
    for realtime in all_realtimes:
        #if realtime.schedule_relationship != ScheduleRelationship.CANCELLED.value:
        realtimes_by_stop[realtime.stop_id].append(realtime)

    all_tripstops = TripStop.objects.filter(trip_id__in=trip_ids).all()
    tripstops_by_stop = defaultdict(list)
    for tripstop in all_tripstops:
        tripstops_by_stop[tripstop.stop_id].append(tripstop)

    for stop_id in set(realtimes_by_stop).union(tripstops_by_stop):
        realtimes = sorted(realtimes_by_stop[stop_id], key=lambda rt: rt.arrival_time)
        tripstops = sorted(tripstops_by_stop[stop_id], key=lambda ts: ts.arrival_time)
        
        if len(tripstops) == 0 or len(realtimes) == 0:
            continue

        day_start = realtimes[0].arrival_time.astimezone(AU_TIMEZONE).replace(hour=4, minute=0)

        route_stop_day = RouteStopDay(route_id=route_id, stop_id=stop_id, date=date)
        route_stop_day.scheduled_bus_count = len(tripstops)
        route_stop_day.realtime_bus_count = len(realtimes)

        wait_times = []
        for tripstop in tripstops:
            scheduled_time = get_datetime_from_36h_string(date, tripstop.arrival_time)
            start_wait = scheduled_time - timedelta(minutes=3)
            for realtime in realtimes:
                if realtime.arrival_time > start_wait:
                    # print(start_wait)
                    # print(realtime.arrival_time)
                    # print((realtime.arrival_time - start_wait))
                    # print((realtime.arrival_time - start_wait).total_seconds())
                    wait_times.append((realtime.arrival_time - start_wait).total_seconds())
                    break

        route_stop_day.schedule_wait_time_seconds_total = sum(wait_times)
        if len(wait_times) != 0:
            route_stop_day.schedule_wait_time_seconds_avg = sum(wait_times) / len(wait_times)
        else:
            route_stop_day.schedule_wait_time_seconds_avg = 0

        # Random wait times for the day
        gaps = []
        for i, realtime in enumerate(realtimes[:-1]):
            gap = (realtime.arrival_time, realtimes[i + 1].arrival_time - realtime.arrival_time)
            gaps.append(gap)
        #print(gaps)

        # Finished the per day metrics
        final_route_stop_day_list.append(route_stop_day)


        if len(realtimes) >= 48:
            hourly_scheduled_bus_count = [0 for i in range(28)]
            for tripstop in tripstops:
                scheduled_time = get_datetime_from_36h_string(date, tripstop.arrival_time)
                delta = int((scheduled_time - day_start).total_seconds() // 3600)
                hourly_scheduled_bus_count[delta] += 1

            hourly_actual_bus_count = [0 for i in range(28)]
            for rt in realtimes:
                delta = int((rt.arrival_time - day_start).total_seconds() // 3600)
                hourly_actual_bus_count[delta] += 1

            rt_weighted_gaps = calculated_weighted_gaps(day_start, [rt.arrival_time for rt in realtimes])
            ts_weighted_gaps = calculated_weighted_gaps(day_start, [get_datetime_from_36h_string(date, ts.arrival_time) for ts in tripstops])

            #for i, thing in enumerate(rt_weighted_gaps):
            #    print(i, thing, sum([t[1] for t in thing]))
            #for i, thing in enumerate(ts_weighted_gaps):
            #    print(i, thing, sum([t[1] for t in thing]))
            # 
            #stop = input('> ')
            for i in range(28):
                route_stop_hour = RouteStopHour(route_id=route_id, stop_id=stop_id, date=date, hour=i)
                route_stop_hour.scheduled_bus_count = hourly_scheduled_bus_count[i]
                route_stop_hour.realtime_bus_count = hourly_actual_bus_count[i]
                route_stop_hour.expected_wait_next_day = is_incomplete_day(ts_weighted_gaps[i])
                route_stop_hour.realtime_wait_next_day = is_incomplete_day(rt_weighted_gaps[i])
                if len(ts_weighted_gaps[i]) != 0:
                    route_stop_hour.expected_random_wait_time_seconds = expected_wait(ts_weighted_gaps[i])
                if len(rt_weighted_gaps[i]) != 0:
                    route_stop_hour.realtime_random_wait_time_seconds = expected_wait(rt_weighted_gaps[i])

                final_route_stop_hour_list.append(route_stop_hour)
    
    #if len(final_route_stop_hour_list)//28 / len(final_route_stop_day_list) > 0.8:
    #    print(route_id)
    #    print('Final stops: ', len(final_route_stop_day_list))
    #    print('Final stop hours: ', len(final_route_stop_hour_list)//28)
    RouteStopDay.objects.filter(route_id=route_id, date=date).delete()
    RouteStopHour.objects.filter(route_id=route_id, date=date).delete()
    RouteStopDay.objects.bulk_create(final_route_stop_day_list)
    RouteStopHour.objects.bulk_create(final_route_stop_hour_list)


def calculate_stop_hour_stats(date, trip_dates_by_route):
    print('Calculating stop route stats for', len(trip_dates_by_route), 'routes')
    for route in trip_dates_by_route:
        calculate_stops(date, route, trip_dates_by_route[route])

