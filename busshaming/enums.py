from enum import Enum


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return tuple((x.value, x.name) for x in cls)


class RouteMetric(ChoiceEnum):
    MOST_ONTIME_TRIP_PERCENT = 1
    LEAST_ONTIME_TRIP_PERCENT = 2
    MOST_EARLY_TRIP_PERCENT = 3
    MOST_VERYLATE_TRIP_PERCENT = 4


class MetricTimespan(ChoiceEnum):
    DAY = 1
    SEVEN_DAYS = 2
    CALENDAR_MONTH = 3
