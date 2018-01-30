import uuid

from django.db import connection, models

from busshaming.enums import RouteMetric, MetricTimespan


UPSERT_ENTRY = '''
INSERT INTO busshaming_routeranking (id, route_id, date, timespan, metric, rank, display_rank, value)
VALUES (uuid_generate_v4(), %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (date, timespan, metric, rank)
DO UPDATE
SET route_id = EXCLUDED.route_id,
    display_rank = EXCLUDED.display_rank,
    value = EXCLUDED.value
'''


class RouteRankingManager(models.Manager):
    def upsert(self, route_id, date, timespan, metric, rank, display_rank, value):
        with connection.cursor() as cursor:
            cursor.execute(UPSERT_ENTRY, (route_id, date, timespan, metric, rank, display_rank, value))


class RouteRanking(models.Model):
    """Denormalization of top N of each different kind of ranking."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    route = models.ForeignKey('Route')
    date = models.DateField(db_index=True)
    timespan = models.PositiveSmallIntegerField(choices=MetricTimespan.choices())
    metric = models.PositiveSmallIntegerField(choices=RouteMetric.choices())
    rank = models.PositiveSmallIntegerField()
    display_rank = models.PositiveSmallIntegerField()
    value = models.FloatField()

    class Meta:
        index_together = (('date', 'timespan', 'metric'),)
        unique_together = (('date', 'timespan', 'metric', 'rank'),)
