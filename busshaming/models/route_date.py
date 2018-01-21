from django.db import models


class RouteDate(models.Model):
    route = models.ForeignKey('Route')
    date = models.DateField(db_index=True)

    num_scheduled_stops = models.PositiveIntegerField()
    num_realtime_stops = models.PositiveIntegerField()
    num_trips = models.PositiveIntegerField()

    # Average realtime coverage/accuracy
    realtime_coverage = models.FloatField(null=True, blank=True)
    realtime_accuracy = models.FloatField(null=True, blank=True)

    early_count = models.IntegerField()
    ontime_count = models.IntegerField()
    late_count = models.IntegerField()
    verylate_count = models.IntegerField()

    count_has_start_middle_end_stats = models.IntegerField(default=False)
    sum_start_delay = models.IntegerField(null=True, blank=True)
    sum_middle_delay = models.IntegerField(null=True, blank=True)
    sum_end_delay = models.IntegerField(null=True, blank=True)

    num_delay_stops = models.PositiveIntegerField()

    sum_delay = models.IntegerField()
    sum_delay_squared = models.BigIntegerField()

    max_delay = models.SmallIntegerField(null=True, blank=True)
    min_delay = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('route', 'date')

    def __str__(self):
        return f'RouteDate {self.route_id} on {self.date}'

    def delay_average(self):
        if self.num_delay_stops != 0:
            return self.sum_delay / self.num_delay_stops
        return None

    def delay_std_dev(self):
        return self.delay_variance() ** 0.5

    def delay_variance(self):
        if self.num_delay_stops != 0:
            return variance(self.num_delay_stops, self.sum_delay, self.sum_delay_squared)
        return None

    def start_delay_average(self):
        if self.count_has_start_middle_end_stats != 0:
            return self.sum_start_delay / self.count_has_start_middle_end_stats

    def middle_delay_average(self):
        if self.count_has_start_middle_end_stats != 0:
            return self.sum_middle_delay / self.count_has_start_middle_end_stats

    def end_delay_average(self):
        if self.count_has_start_middle_end_stats != 0:
            return self.sum_end_delay / self.count_has_start_middle_end_stats


def variance(count, summed, summed_squares):
    return (summed_squares - (summed * summed / count)) / count
