import uuid

from django.db import connection, models

UPSERT_ENTRY = '''
INSERT INTO busshaming_realtimeentry (id, trip_date_id, stop_id, sequence, arrival_time, arrival_delay, departure_time, departure_delay)
VALUES (uuid_generate_v4(), %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (trip_date_id, stop_id)
DO UPDATE
SET sequence = EXCLUDED.sequence,
    arrival_time = EXCLUDED.arrival_time,
    arrival_delay = EXCLUDED.arrival_delay,
    departure_time = EXCLUDED.departure_time,
    departure_delay = EXCLUDED.departure_delay
'''


class RealtimeEntryManager(models.Manager):
    def upsert(self, trip_date_id, stop_id, sequence, arrival_time, arrival_delay, departure_time, departure_delay):
        with connection.cursor() as cursor:
            cursor.execute(UPSERT_ENTRY, (trip_date_id, stop_id, sequence, arrival_time, arrival_delay, departure_time, departure_delay))


class RealtimeEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    trip_date = models.ForeignKey('TripDate')
    stop = models.ForeignKey('Stop')
    sequence = models.IntegerField()
    arrival_time = models.DateTimeField()
    arrival_delay = models.SmallIntegerField()
    departure_time = models.DateTimeField()
    departure_delay = models.SmallIntegerField()

    objects = RealtimeEntryManager()

    class Meta:
        unique_together = ('trip_date', 'stop')

    def __str__(self):
        return f'{self.id} (stop {self.sequence} at stop id {self.stop_id})'
