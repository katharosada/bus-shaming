package net.katiebell.busshaming.fetcher;

import com.datastax.driver.core.ResultSet;
import com.datastax.driver.core.Row;
import com.datastax.driver.core.Session;
import com.datastax.driver.core.querybuilder.QueryBuilder;
import com.datastax.driver.core.querybuilder.Select;
import com.datastax.driver.mapping.annotations.Query;

import java.util.*;

/**
 * Created by katharos on 14/05/2017.
 */
public class Trip {
  private UUID tripUuid;
  private UUID feedUuid;
  private String routeId;
  private String tripId;
  private DayOfWeek dayOfWeek;
  private String startTime;
  private int direction;
  private String headsign;

  public UUID getTripUuid() {
    return tripUuid;
  }

  public UUID getFeedUuid() {
    return feedUuid;
  }

  public String getRouteId() {
    return routeId;
  }

  public String getTripId() {
    return tripId;
  }

  public DayOfWeek getDayOfWeek() {
    return dayOfWeek;
  }

  public String getStartTime() {
    return startTime;
  }

  public int getDirection() {
    return direction;
  }

  public String getHeadsign() {
    return headsign;
  }

  public Trip(UUID tripUuid, UUID feedUuid, String tripId, String routeId, DayOfWeek dayOfWeek, String startTime, int direction, String headsign) {
    this.tripUuid = tripUuid;
    this.feedUuid = feedUuid;
    this.routeId = routeId;
    this.tripId = tripId;
    this.dayOfWeek = dayOfWeek;
    this.startTime = startTime;
    this.direction = direction;
    this.headsign = headsign;
  }

  public enum DayOfWeek {
    monday(0),
    tuesday(1),
    wednesday(2),
    thursday(3),
    friday(4),
    saturday(5),
    sunday(6),;

    private final int value;
    private static Map<String, DayOfWeek> nameMap = new HashMap<>();

    DayOfWeek(int val) {
      value = val;
    }

    public int getValue() {
      return value;
    }

    static DayOfWeek getValueOrNull(String name) {
      if (nameMap.containsKey(name)) {
        return nameMap.get(name);
      }
      DayOfWeek[] values = values();
      for (int i = 0; i < values.length; i++) {
        if (values[i].name().equals(name)) {
          nameMap.put(name, values[i]);
          return values[i];
        }
      }
      return null;
    }
  }

  static List<Trip> fetchTripsForRoute(Session session, UUID feedUuid, String routeId) {
    List<Trip> trips = new ArrayList<>();
    Select selectTrips = QueryBuilder.select("trip_uuid", "trip_id", "day_of_week", "start_time", "direction", "trip_headsign")
            .from("busshaming", "Trip")
            .where(QueryBuilder.eq("route_id", routeId))
              .and(QueryBuilder.eq("feed_uuid", feedUuid))
            .orderBy(QueryBuilder.asc("day_of_week"), QueryBuilder.asc("start_time"))
            .allowFiltering();
    ResultSet results = session.execute(selectTrips);
    for (Row row : results) {
      UUID tripUuid = row.getUUID(0);
      String tripId = row.getString(1);
      DayOfWeek dayOfWeek = DayOfWeek.values()[row.getInt(2)];
      String startTime = row.getString(3);
      int direction = row.getInt(4);
      String headsign = row.getString(5);
      Trip trip = new Trip(tripUuid, feedUuid, tripId, routeId, dayOfWeek, startTime, direction, headsign);
      trips.add(trip);
    }
    return trips;
  }


}
