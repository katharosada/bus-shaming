from datetime import datetime

from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie

from busshaming.models import Route, TripDate

DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']


@ensure_csrf_cookie
def route_by_date(request, route_id, datestr):
    date = datetime.strptime(datestr, '%Y%m%d').date()
    route = get_object_or_404(Route, id=route_id)
    trip_dates = TripDate.objects.filter(date=date, trip__route=route)
    data = {'route': route, 'trip_dates': trip_dates}
    return render(request, 'route_by_date.html', context=data)
