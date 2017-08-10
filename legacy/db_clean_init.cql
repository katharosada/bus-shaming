// Keyspace
DROP KEYSPACE IF EXISTS busshaming;
CREATE KEYSPACE busshaming
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor' : 1};


USE busshaming;

//
DROP TABLE IF EXISTS TransportFeed;
DROP TABLE IF EXISTS Route;
DROP TABLE IF EXISTS Trip;
DROP TABLE IF EXISTS Run;


CREATE TABLE TransportFeed (
  feed_uuid uuid,
  feed_url text,
  city text,
  state text,
  country text,
  PRIMARY KEY (feed_uuid)
);

CREATE TABLE Route (
  feed_uuid uuid,
  agency_id text,
  route_id text,
  short_name text,
  long_name text,
  description text,
  route_type int,
  color text,
  text_color text,
  PRIMARY KEY (feed_uuid, route_id)
);

// A trip on the schedule
CREATE TABLE Trip (
  trip_uuid uuid,
  feed_uuid uuid,
  route_id text,
  trip_id text,
  direction int,
  day_of_week int,
  trip_headsign text,
  start_time text,
  PRIMARY KEY ((feed_uuid, route_id), day_of_week, start_time, trip_id),
);

CREATE TABLE Run (
  trip_uuid uuid,
  year int,
  avg_delay int,
  std_dev int,
  max_delay int,
  on_time int,
  stop_count int,
  early_count int,
  late_count int,
  very_late_count int,
  ridiculous_count int,
  start_date date,
  stop_times Map<text, time>,
  delays Map<text, int>,
  PRIMARY KEY ((trip_uuid, year), start_date)
);
