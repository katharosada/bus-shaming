from collections import defaultdict
import sys
import django
django.setup()

from busshaming.models import Route, RouteDate

from datetime import date

switch_date = date(2018, 7, 1)

def get_stats(routedates):
    days = set(rd.date for rd in routedates)
    num_trips = sum(rd.num_trips for rd in routedates)

    ontime = sum([rd.trip_ontime_count for rd in routedates])
    verylate = sum([rd.trip_verylate_count for rd in routedates])

    stats = {
        'days': len(days),
        'num_trips': num_trips,
        'trips per day': num_trips / len(days),
        'ontime': ontime,
        'late': sum([rd.trip_late_count for rd in routedates]),
        'verylate': verylate,
        'early': sum([rd.trip_early_count for rd in routedates]),
        'ontime percent': 100 * ontime / num_trips,
        'verylate percent': 100 * verylate / num_trips,
    }
    return stats

def main(routes):
    before_routedates = RouteDate.objects.filter(route__in=routes, date__lt=switch_date).all()
    after_routedates = RouteDate.objects.filter(route__in=routes, date__gte=switch_date).all()

    before_stats = get_stats(before_routedates)
    after_stats = get_stats(after_routedates)

    for stat in before_stats:
        print(stat)
        print(before_stats[stat], '\t', after_stats[stat])


if __name__ == '__main__':
    ids = [int(l.strip()) for l in open('scripts/inner_west_routes.txt')]
    routes = Route.objects.filter(id__in=ids)
    main(routes)