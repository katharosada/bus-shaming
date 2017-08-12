from django.db import models


class TripTimetable(models.Model):
    trip = models.ForeignKey('Trip')
    start_date = models.DateField()
    end_date = models.DateField()
    monday = models.BooleanField()
    tuesday = models.BooleanField()
    wednesday = models.BooleanField()
    thursday = models.BooleanField()
    friday = models.BooleanField()
    saturday = models.BooleanField()
    sunday = models.BooleanField()
