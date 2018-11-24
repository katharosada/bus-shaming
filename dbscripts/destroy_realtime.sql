# Destroy all realtime data (for reprocessing)
# But keep the timetable content around.

TRUNCATE busshaming_realtimeentry RESTART IDENTITY;
TRUNCATE busshaming_realtimeprogress RESTART IDENTITY;
TRUNCATE busshaming_routedate RESTART IDENTITY;
TRUNCATE busshaming_routeranking RESTART IDENTITY;

# Stops from trips which were realtime added
DELETE FROM busshaming_tripstop
WHERE trip_id in (
	SELECT id from busshaming_trip
	WHERE added_from_realtime = true
);

# Tripdates for trips that were realtime added.
DELETE FROM busshaming_tripdate
WHERE trip_id in (
	SELECT id from busshaming_trip
	WHERE added_from_realtime = true
);

DELETE FROM busshaming_trip
WHERE added_from_realtime = true;

DELETE FROM busshaming_tripdate
WHERE added_from_realtime = true;


UPDATE busshaming_tripdate
SET is_stats_calculation_done = false;