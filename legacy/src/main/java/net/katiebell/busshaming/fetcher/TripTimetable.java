package net.katiebell.busshaming.fetcher;

import com.datastax.driver.core.Cluster;
import com.datastax.driver.core.ResultSet;
import com.datastax.driver.core.Session;
import com.datastax.driver.core.Statement;
import com.datastax.driver.core.querybuilder.*;
import com.opencsv.CSVReader;

import java.io.IOException;
import java.util.*;

/**
 * Created by katharos on 23/04/2017.
 */
public class TripTimetable {

  private Map<String, Set<Trip.DayOfWeek>> serviceCalendar = new HashMap<>();
  private Map<String, Map<String, Object>> tripDetails = new HashMap<>();
  private Map<String, Map<String, String>> tripStops = new HashMap<>();
  private Map<String, Object> startTimes = new HashMap<>();

  public TripTimetable() {}

  public void processCalendarData(CSVReader csvReader) throws IOException {
    System.out.println("Processing calendar.txt data");
    String [] nextLine;
    String[] titles = csvReader.readNext();
    while ((nextLine = csvReader.readNext()) != null) {
      String serviceID = null;
      Set<Trip.DayOfWeek> days = new HashSet<>();
      for (int i = 0; i < nextLine.length; i++) {
        String column = titles[i];
        String value = nextLine[i];
        if (column.equals("service_id")) {
          serviceID = value;
        }
        Trip.DayOfWeek day = Trip.DayOfWeek.getValueOrNull(column);
        if (day != null && Integer.parseInt(value) == 1) {
          days.add(day);
        }
      }
      if (serviceID != null) {
        serviceCalendar.put(serviceID, days);
      }
    }
  }

  public void processTripData(CSVReader csvReader) throws IOException {
    System.out.println("Processing trips.txt data");
    String [] nextLine;
    String[] titles = csvReader.readNext();
    while ((nextLine = csvReader.readNext()) != null) {
      Map<String, Object> trip = new HashMap<>();
      for (int i = 0; i < nextLine.length; i++) {
        String column = titles[i];
        String value = nextLine[i];
        switch (column) {
          case "trip_id":
          case "route_id":
          case "service_id":
          case "trip_headsign":
            trip.put(column, value);
            break;
          case "direction_id":
            trip.put("direction", Integer.parseInt(value));
            break;
          default:
            break;
            //System.out.println("Ignoring column: " + column);
        }
      }
      mergeTripDetails(trip);
    }
  }

  private void mergeTripDetails(Map<String, Object> newDetails) {
    String tripId = (String) newDetails.get("trip_id");

    if (tripDetails.containsKey(tripId)) {
      Map<String, Object> existing = tripDetails.get(tripId);
      for (Map.Entry<String, Object> entry : newDetails.entrySet()) {
        existing.put(entry.getKey(), entry.getValue());
      }
    } else {
      tripDetails.put(tripId, newDetails);
    }
  }

  public void processStopTimeData(CSVReader csvReader) throws IOException {
    System.out.println("Processing stop_times.txt data");
    String [] nextLine;
    String[] titles = csvReader.readNext();
    while ((nextLine = csvReader.readNext()) != null) {
      Map<String, Object> trip = new HashMap<>();
      boolean isStartingStop = false;
      String time = null;
      for (int i = 0; i < nextLine.length; i++) {
        String column = titles[i];
        String value = nextLine[i];
        switch (column) {
          case "trip_id":
            trip.put(column, value);
            break;
          case "stop_sequence":
            int stopNo = Integer.parseInt(value);
            if (stopNo == 1) {
              isStartingStop = true;
            }
            break;
          case "arrival_time":
            time = value;
            break;
          default:
            //System.out.println("Igoring column: " + column);
            break;
        }
      }
      if (isStartingStop) {
        trip.put("start_time", time);
        mergeTripDetails(trip);
      }
    }
  }

  public void updateDatabase(Session session, UUID feedUuid) {
    System.out.println("Updating database with " + tripDetails.size() + " trips.");

    for (Map.Entry<String, Map<String, Object>> tripEntry : tripDetails.entrySet()) {
      String trip_id = tripEntry.getKey();
      Map<String, Object> trip = tripEntry.getValue();
      String service_id = (String) trip.get("service_id");
      Set<Trip.DayOfWeek> days = serviceCalendar.get(service_id);
      for (Trip.DayOfWeek dayOfWeek : days) {
        UUID tripUuid = UUID.randomUUID();
        Insert insert = QueryBuilder.insertInto("busshaming", "trip")
                .value("trip_id", trip_id)
                .value("route_id", trip.get("route_id"))
                .value("feed_uuid", feedUuid)
                .value("day_of_week", dayOfWeek.getValue())
                .value("start_time", trip.get("start_time"))
                .value("trip_uuid", tripUuid)
                .ifNotExists();

        ResultSet rs = session.execute(insert);
        if (!rs.wasApplied()) {
          // Probably means the trip already existed, so we need to fetch the correct uuid.
          tripUuid = null;
        }
        Statement update = QueryBuilder.update("busshaming", "trip")
                .with(QueryBuilder.set("direction", trip.get("direction")))
                .and(QueryBuilder.set("trip_headsign", trip.get("trip_headsign")))
                .where(QueryBuilder.eq("trip_id", trip_id))
                .and(QueryBuilder.eq("route_id", trip.get("route_id")))
                .and(QueryBuilder.eq("feed_uuid", feedUuid))
                .and(QueryBuilder.eq("day_of_week", dayOfWeek.getValue()))
                .and(QueryBuilder.eq("start_time", trip.get("start_time")));
        session.execute(update);
      }
    }
  }
}
