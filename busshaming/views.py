from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from busshaming import fetching


@ensure_csrf_cookie
def index(request):
    return render(request, 'index.html')


@ensure_csrf_cookie
def fetch_timetable(request):
    fetching.fetch_timetable()
    return render(request, 'index.html')
