from collections import defaultdict
import sys
import django
django.setup()

from busshaming.models import Agency, RouteDate, Feed

FEED_SLUG = 'nsw-buses'


MIN_TRIPS = 500
MIN_RT_ENTRIES = 0


def main(is_best, verylate):
    feed = Feed.objects.get(slug=FEED_SLUG)
    routedates = defaultdict(list)
    for rd in RouteDate.objects.filter(route__feed=feed).prefetch_related('route').all():
        routedates[rd.route.agency.name].append(rd)

    results = []
    for agency_name in routedates:
        rds = routedates[agency_name]
        num_trips = sum([rd.num_scheduled_trips for rd in rds])
        if num_trips == 0:
            continue
        total_ontime = sum([rd.scheduled_trip_ontime_count for rd in rds])
        total_verylate = sum([rd.scheduled_trip_verylate_count for rd in rds])
        if num_trips < MIN_TRIPS:
            continue
        result = [
            agency_name,
            num_trips,
            100 * total_ontime / num_trips,
            100 * total_verylate / num_trips,
        ]
        results.append(result)

    if verylate:
        results.sort(key=lambda x: x[3], reverse=not best)
    else:
        results.sort(key=lambda x: x[2], reverse=best)

    for i, res in enumerate(results):
        desc = res[0]
        out = f'{i+1}\t{res[1]}\t{res[2]:.2f}\t{res[3]:.2f}\t' + desc
        print(out)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f'Usage: {sys.argv[0]} <best|worst> <ontime|verylate>')
        sys.exit(1)

    best = sys.argv[1] == 'best'
    verylate = sys.argv[2] == 'verylate'

    main(best, verylate)
