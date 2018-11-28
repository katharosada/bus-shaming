from collections import defaultdict
import sys
import django
django.setup()

from busshaming.models import RouteDate, Feed

FEED_SLUG = 'nsw-buses'


# 322 days of data at 4 trips/day on average
MIN_TRIPS = 322 * 4
MIN_RT_ENTRIES = 0


def main(is_best, verylate):
    feed = Feed.objects.get(slug=FEED_SLUG)
    routedates = defaultdict(list)
    for rd in RouteDate.objects.filter(route__feed=feed).prefetch_related('route').all():
        routedates[rd.route_id].append(rd)

    global_trip_count = 0
    global_ontime = 0
    global_verylate = 0

    results = []
    for route_id in routedates:
        route = routedates[route_id][0].route
        rds = routedates[route_id]
        num_trips = sum([rd.num_trips for rd in rds])
        if num_trips == 0:
            continue
        total_ontime = sum([rd.trip_ontime_count for rd in rds])
        total_verylate = sum([rd.trip_verylate_count for rd in rds])
        global_trip_count += num_trips
        global_ontime += total_ontime
        global_verylate += total_verylate
        if num_trips < MIN_TRIPS:
            continue
        result = [
            route.id,
            num_trips,
            100 * total_ontime / num_trips,
            100 * total_verylate / num_trips,
            route.short_name,
            route.long_name,
            route.agency.name,
        ]
        results.append(result)

    if verylate:
        results.sort(key=lambda x: x[3], reverse=not best)
    else:
        results.sort(key=lambda x: x[2], reverse=best)

    for i in range(50):
        res = results[i]
        desc = '\t'.join(res[4:])
        out = f'{i+1}\t{res[1]}\t{res[2]:.2f}\t{res[3]:.2f}\t' + desc
        print(out)

    print()
    print('Totals:')
    print(f'Num trips: {global_trip_count}')
    print(f'Ontime: {global_ontime} ({100 * global_ontime / global_trip_count :.2f}%)')
    print(f'Very late: {global_verylate} ({100 * global_verylate / global_trip_count :.2f}%)')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f'Usage: {sys.argv[0]} <best|worst> <ontime|verylate>')
        sys.exit(1)

    best = sys.argv[1] == 'best'
    verylate = sys.argv[2] == 'verylate'

    main(best, verylate)
