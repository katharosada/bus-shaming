from datetime import timedelta
from statistics import mean, median
from collections import defaultdict

import pytz

from busshaming.models import TripDate, TripStop, RealtimeEntry, RouteDate

AU_TIMEZONE = pytz.timezone('Australia/Sydney')

meta_stats = {}


def get_hour_minute_from_36h_string(timestr):
    hour, minute, second = [int(s) for s in timestr.split(':')]
    if hour >= 24:
        hour -= 24
    return hour, minute


def is_time_match(tripstop, realtime):
    realtime_arrival = (realtime.arrival_time - timedelta(seconds=realtime.arrival_delay)).astimezone(AU_TIMEZONE)
    hour, minute = get_hour_minute_from_36h_string(tripstop.arrival_time)
    expected_arrival = realtime_arrival.replace(hour=hour, minute=minute)
    if abs(realtime_arrival - expected_arrival) >= timedelta(minutes=2):
        hour, minute = get_hour_minute_from_36h_string(tripstop.departure_time)
        expected_arrival = realtime_arrival.replace(hour=hour, minute=minute)
        if abs(realtime_arrival - expected_arrival) >= timedelta(minutes=2):
            return False
    return True


def validate_tripstop_and_realtime(trip_stops, realtimes):
    '''
    Returns Score for:
    - Percentage realtime coverage (% of scheduled stop with realtime data)
    - Precentage realtime accuracy (% of realtime stops which matched schedule)
    And list of errors
    '''

    original_realtimes_len = len(realtimes)
    has_realtime = 0
    realtime_mismatch = 0

    errors = []
    realtime_shift = 0
    stop_zeros = {}
    while len(realtimes) != 0:
        if realtimes[0].sequence == 0:
            stop_zeros[realtimes[0].stop_id] = realtimes[0]
            realtimes.pop(0)
        else:
            break

    trip_stop_i = 0
    realtime_i = 0
    while trip_stop_i < len(trip_stops) and realtime_i < len(realtimes):
        ts = trip_stops[trip_stop_i]
        r = realtimes[realtime_i]
        if ts.sequence == r.sequence + realtime_shift:
            # Check stop matches
            if ts.stop_id != r.stop_id:
                # Sometimes the realtime sequence is offset from the timetable
                if trip_stop_i + 1 < len(trip_stops) and trip_stops[trip_stop_i + 1].stop_id == realtimes[realtime_i].stop_id:
                    realtime_shift += 1
                    realtime_mismatch += 1
                    continue
                elif realtime_i + 1 < len(realtimes) and trip_stops[trip_stop_i].stop_id == realtimes[realtime_i + 1].stop_id:
                    realtime_i += 1
                    realtime_shift -= 1
                    realtime_mismatch += 1
                    continue
                else:
                    realtime_mismatch += 1
                    errors.append(f'Stop mismatch sequence {ts.sequence} was ts {ts.stop_id} but realtime was {r.stop_id}')
            elif not is_time_match(ts, r):
                realtime_mismatch += 1
                errors.append(f'Time mismatch sequence {ts.sequence}. {r} vs {ts}')
            else:
                has_realtime += 1
            realtime_i += 1
            trip_stop_i += 1
        else:
            if ts.sequence < r.sequence + realtime_shift:
                # Try to find the stop in the zeros list
                if ts.stop_id in stop_zeros:
                    new_r = stop_zeros[ts.stop_id]
                    if is_time_match(ts, new_r):
                        del stop_zeros[ts.stop_id]
                        new_r.sequence = ts.sequence - realtime_shift
                        realtimes.append(new_r)
                        realtimes.sort(key=lambda r: r.sequence)
                    else:
                        has_realtime += 1
                        trip_stop_i += 1
                else:
                    trip_stop_i += 1
            else:
                realtime_i += 1
                realtime_mismatch += 1
                errors.append(f'Missing trip stop for sequence {r.sequence} stop {r.stop_id}')

    while trip_stop_i < len(trip_stops):
        ts = trip_stops[trip_stop_i]
        if ts.stop_id in stop_zeros:
            new_r = stop_zeros[ts.stop_id]
            if is_time_match(ts, new_r):
                del stop_zeros[ts.stop_id]
                new_r.sequence = ts.sequence - realtime_shift
                realtimes.append(new_r)
                realtimes.sort(key=lambda r: r.sequence)
                has_realtime += 1
        trip_stop_i += 1

    for stop in stop_zeros:
        realtime_mismatch += 1

    return has_realtime / len(trip_stops), (original_realtimes_len - realtime_mismatch) / original_realtimes_len, errors


def calculate_tripdate_stats(trip_date):
    realtime_entries = list(RealtimeEntry.objects.filter(trip_date=trip_date).order_by('sequence').all())
    trip_stops = list(TripStop.objects.filter(trip_id=trip_date.trip_id).order_by('sequence').all())

    # Calculate denormalized data
    trip_date.num_scheduled_stops = len(trip_stops)
    trip_date.num_realtime_stops = len(realtime_entries)
    if len(trip_stops) > 0:
        trip_date.start_time = trip_stops[0].arrival_time
    else:
        meta_stats['no_tripstops'] += 1

    if len(realtime_entries) == 0:
        # We're done here
        meta_stats['no_realtimeentries'] += 1
        trip_date.realtime_coverage = 0
        trip_date.realtime_accuracy = None
        trip_date.has_realtime_stats = False
        trip_date.is_stats_calculation_done = True
        trip_date.save()
        return

    if len(trip_stops) > 0:
        realtime_coverage, realtime_accuracy, errors = validate_tripstop_and_realtime(trip_stops, realtime_entries)
        if errors:
            if trip_date.added_from_realtime or trip_date.trip.added_from_realtime:
                print('Added from realtime')
            else:
                print('NOT ADDED FROM REALTIME')
            print('TripDate', trip_date.id)
            print('Trip', trip_date.trip_id)
            print(trip_stops)
            print(realtime_entries)
            for error in errors:
                print(error)
            meta_stats['irreconcileable_stop_mismatch'] += 1
        trip_date.realtime_coverage = realtime_coverage
        if realtime_coverage < 0.9:
            meta_stats['poor_coverage'] += 1
        trip_date.realtime_accuracy = realtime_accuracy
        if realtime_accuracy < 0.9:
            meta_stats['poor_accuracy'] += 1
        if realtime_coverage == 1.0 and realtime_accuracy == 1.0:
            meta_stats['perfect_match'] += 1

    trip_date.has_start_middle_end_stats = False
    if len(trip_stops) != 0:
        middle_sequence = trip_stops[len(trip_stops)//2].sequence
        # start, middle, end delay (using timing stops)
        timing_stops = [ts for ts in trip_stops if ts.timepoint]
        if len(timing_stops) == 0:
            meta_stats['no_timepoints'] += 1
        elif len(timing_stops) < 3:
            meta_stats['not_enough_timepoints'] += 1
        else:
            start_rt = get_matching_realtime(realtime_entries, timing_stops[0])
            middle_rt = get_matching_realtime(realtime_entries, min(timing_stops, key=lambda ts: abs(ts.sequence - middle_sequence)))
            end_rt = get_matching_realtime(realtime_entries, timing_stops[-1])
            if start_rt and middle_rt and end_rt:
                trip_date.start_delay = start_rt.arrival_delay
                trip_date.middle_delay = middle_rt.arrival_delay
                trip_date.end_delay = end_rt.arrival_delay
                trip_date.has_start_middle_end_stats = True
                meta_stats['has_start_middle_end'] += 1

    delays = []
    total_delay = 0
    total_delay_squared = 0
    for rt in realtime_entries:
        delay = max(rt.arrival_delay, rt.departure_delay)
        delays.append(delay)
        total_delay += delay
        total_delay_squared += delay * delay

    delays.sort()
    trip_date.max_delay = delays[-1]
    trip_date.min_delay = delays[0]
    trip_date.median_delay = median(delays)
    if len(delays) >= 2:
        trip_date.lower_quartile_delay = median(delays[:len(delays)//2])
        trip_date.upper_quartile_delay = median(delays[len(delays)//2:])
    else:
        trip_date.lower_quartile_delay = trip_date.median_delay
        trip_date.upper_quartile_delay = trip_date.median_delay

    trip_date.early_count = sum(delay < -2 * 60 for delay in delays)
    trip_date.ontime_count = sum(-2 * 60 <= delay <= 5 * 60 for delay in delays)
    trip_date.late_count = sum(5 * 60 < delay <= 20 * 60 for delay in delays)
    trip_date.verylate_count = sum(delay > 20 * 60 for delay in delays)

    trip_date.num_delay_stops = len(realtime_entries)
    trip_date.avg_delay = total_delay / len(realtime_entries)
    trip_date.variance_delay = variance(len(realtime_entries), total_delay, total_delay_squared)
    trip_date.sum_delay = total_delay
    trip_date.sum_delay_squared = total_delay_squared

    trip_date.has_realtime_stats = True
    trip_date.is_stats_calculation_done = True
    trip_date.save()


def variance(count, summed, summed_squares):
    return (summed_squares - (summed * summed / count)) / count


def get_matching_realtime(realtime_entries, trip_stop):
    for r in realtime_entries:
        if r.sequence == trip_stop.sequence and r.stop_id == trip_stop.stop_id:
            return r
    # Sometimes the sequence if off by 1 or 2
    for r in realtime_entries:
        if r.stop_id == trip_stop.stop_id and abs(r.sequence - trip_stop.sequence) <= 2:
            return r
    return None


def calculate_route_date_stats(date):
    trip_dates_by_route = defaultdict(list)
    for tripdate in TripDate.objects.filter(date=date).prefetch_related('trip').all():
        trip_dates_by_route[tripdate.trip.route_id].append(tripdate)

    for route_id in trip_dates_by_route:
        trip_dates = trip_dates_by_route[route_id]

        try:
            route_date = RouteDate.objects.get(route_id=route_id, date=date)
        except RouteDate.DoesNotExist:
            route_date = RouteDate(route_id=route_id, date=date)

        route_date.num_trips = len(trip_dates)
        route_date.num_scheduled_trips = len([td for td in trip_dates if not td.added_from_realtime])
        route_date.num_scheduled_stops = 0
        route_date.num_realtime_stops = 0
        route_date.early_count = 0
        route_date.ontime_count = 0
        route_date.late_count = 0
        route_date.verylate_count = 0
        route_date.count_has_start_middle_end_stats = 0
        route_date.sum_start_delay = 0
        route_date.sum_middle_delay = 0
        route_date.sum_end_delay = 0
        route_date.num_delay_stops = 0
        route_date.sum_delay = 0
        route_date.sum_delay_squared = 0

        route_date.trip_early_count = 0
        route_date.trip_ontime_count = 0
        route_date.trip_late_count = 0
        route_date.trip_verylate_count = 0
        route_date.scheduled_trip_early_count = 0
        route_date.scheduled_trip_ontime_count = 0
        route_date.scheduled_trip_late_count = 0
        route_date.scheduled_trip_verylate_count = 0

        for tripdate in trip_dates:
            route_date.num_scheduled_stops += tripdate.num_scheduled_stops
            route_date.num_realtime_stops += tripdate.num_realtime_stops

            if tripdate.num_realtime_stops > 0:
                route_date.early_count += tripdate.early_count
                route_date.ontime_count += tripdate.ontime_count
                route_date.late_count += tripdate.late_count
                route_date.verylate_count += tripdate.verylate_count
                route_date.num_delay_stops += tripdate.num_delay_stops
                route_date.sum_delay += tripdate.sum_delay
                route_date.sum_delay_squared += tripdate.sum_delay_squared

                early = tripdate.early_count > 0
                late = tripdate.late_count > 0
                verylate = tripdate.verylate_count > 0
                ontime = not (early or late or verylate)

                route_date.trip_early_count += early
                route_date.trip_ontime_count += ontime
                route_date.trip_late_count += late
                route_date.trip_verylate_count += verylate

                if not tripdate.added_from_realtime:
                    route_date.scheduled_trip_early_count += early
                    route_date.scheduled_trip_ontime_count += ontime
                    route_date.scheduled_trip_late_count += late
                    route_date.scheduled_trip_verylate_count += verylate

            if tripdate.has_start_middle_end_stats:
                route_date.count_has_start_middle_end_stats += 1
                route_date.sum_start_delay += tripdate.start_delay
                route_date.sum_middle_delay += tripdate.middle_delay
                route_date.sum_end_delay += tripdate.end_delay

        if route_date.num_delay_stops > 0:
            route_date.max_delay = max(td.max_delay for td in trip_dates if td.max_delay is not None)
            route_date.min_delay = min(td.min_delay for td in trip_dates if td.min_delay is not None)

            route_date.ontime_percent = route_date.ontime_count / route_date.num_delay_stops

        route_date.trip_ontime_percent = route_date.trip_ontime_count / route_date.num_trips

        if route_date.num_scheduled_stops > 0:
            route_date.realtime_coverage = mean(td.realtime_coverage for td in trip_dates if td.realtime_coverage is not None)
            accuracies = [td.realtime_accuracy for td in trip_dates if td.realtime_accuracy is not None]
            if len(accuracies) > 0:
                route_date.realtime_accuracy = mean(accuracies)
            else:
                route_date.realtime_accuracy = None

        if route_date.num_scheduled_trips > 0:
            route_date.scheduled_trip_ontime_percent = route_date.scheduled_trip_ontime_count / route_date.num_scheduled_trips

        route_date.save()


def calculate_stats_for_day(date):
    global meta_stats
    meta_stats = {
        'trip_dates_processed': 0,
        'perfect_match': 0,
        'poor_coverage': 0,
        'poor_accuracy': 0,
        'no_tripstops': 0,
        'no_realtimeentries': 0,
        'no_timepoints': 0,
        'not_enough_timepoints': 0,
        'has_start_middle_end': 0,
        'irreconcileable_stop_mismatch': 0,
    }
    tripdates = TripDate.objects.filter(date=date, is_stats_calculation_done=False).prefetch_related('trip')
    total = tripdates.count()
    milestone = total // 10
    for i, tripdate in enumerate(tripdates):
        if i % milestone == 1:
            percent = int(i/total*100)
            print(f'{i} out of {total} ({percent}%)')
        calculate_tripdate_stats(tripdate)
        meta_stats['trip_dates_processed'] += 1
    for stat in meta_stats:
        print(f'{stat}: {meta_stats[stat]}')
    calculate_route_date_stats(date)
