package net.katiebell.busshaming.fetcher;

import com.datastax.driver.core.*;
import com.datastax.driver.core.querybuilder.Insert;
import com.datastax.driver.core.querybuilder.QueryBuilder;
import com.datastax.driver.mapping.annotations.Query;
import com.fasterxml.jackson.databind.util.ClassUtil;
import com.google.transit.realtime.GtfsRealtime;
import com.opencsv.CSVParser;
import com.opencsv.CSVReader;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.Calendar;
import java.util.Date;
import java.util.Scanner;
import java.util.UUID;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/**
 * Created by katharos on 18/04/2017.
 */
@Component
public class Fetcher {

  private static final int FETCH_PERIOD = 2 * 60 * 1000; // 2min
  private static final String BUS_REALTIME_URL = "https://api.transport.nsw.gov.au/v1/gtfs/realtime/buses/";
  private static final String BUS_SCHEDULE_URL = "https://api.transport.nsw.gov.au/v1/gtfs/schedule/buses/";
  private static final String API_KEY_HEADER_NAME = "Authorization";
  private static final String API_KEY = System.getenv("GTFS_API_KEY");
  private static final String API_KEY_HEADER_CONTENTS = "apikey " + API_KEY;

  static Date lastFetch = null;
  static String latestBus = "";
  static String latestStop = "";
  static int latestDelay = 0;

  // Magic uuid in the theory that this will eventually support multiple gtfs feeds
  public static final UUID SYDNEY_BUSSES_UUID = UUID.fromString("c991da41-68bd-43d4-b71b-8d82b16e46d0");
  private static final String SYDNEY_INSERT = "" +
          "INSERT INTO busshaming.transportfeed (feed_uuid, feed_url, city, state, country) VALUES " +
          "(" + SYDNEY_BUSSES_UUID + ", '" + BUS_SCHEDULE_URL + "', 'Sydney', 'NSW', 'Australia') " +
          "IF NOT EXISTS WITH CONSISTENCY ONE";



  @Scheduled(fixedDelay = FETCH_PERIOD)
  public void fetchRealtime() {
    String query = QueryBuilder.insertInto("busshaming", "transportfeed")
            .values(new String[]{"feed_uuid", "feed_url", "city", "state", "country"},
                    new Object[]{SYDNEY_BUSSES_UUID, BUS_SCHEDULE_URL, "Sydney", "NSW", "Australia"})
            .ifNotExists()
            .toString();
    System.out.println(query);
    Session session = Cassandra.getSession();
    ResultSet rs = session.execute(query);
    System.out.println("Was applied: " + rs.wasApplied());

    //fetchUpdatedTimetable();
    fetchCurrentDelays();
    Calendar calendar = Calendar.getInstance();
    lastFetch = calendar.getTime();
  }

  private void fetchUpdatedTimetable() {
    // Fetch agencies.txt (?)
    Session session = Cassandra.getSession();
    ZipInputStream timetableZip;
    try {
      timetableZip = fetchTimetableZip(BUS_SCHEDULE_URL);

      ZipEntry entry;
      TripTimetable timetable = new TripTimetable();
      while((entry = timetableZip.getNextEntry()) != null) {
        String name = entry.getName();
        System.out.println(name);
        if (name.equals("calendar.txt")) {
          timetable.processCalendarData(new CSVReader(new InputStreamReader(timetableZip)));
        } else if (name.equals("stop_times.txt")) {
          timetable.processStopTimeData(new CSVReader(new InputStreamReader(timetableZip)));
        } else if (name.equals("trips.txt")) {
          timetable.processTripData(new CSVReader(new InputStreamReader(timetableZip)));
        } else if (name.equals("routes.txt")) {
          CSVReader csvReader = new CSVReader(new InputStreamReader(timetableZip));
          String [] nextLine;
          String[] titles = csvReader.readNext();

          while ((nextLine = csvReader.readNext()) != null) {
            Insert query = QueryBuilder.insertInto("busshaming", "route");
            query = query.value("feed_uuid", SYDNEY_BUSSES_UUID);
            String route_id = "unknown";
            for (int i = 0; i < nextLine.length; i++) {
              String column = titles[i];
              String value = nextLine[i];
              switch (column) {
                case "route_id":
                  route_id = value;
                  query.value(column, value);
                  break;
                case "agency_id":
                  query.value(column, value);
                  break;
                case "route_short_name":
                  query.value("short_name", value);
                  break;
                case "route_long_name":
                  query.value("long_name", value);
                  break;
                case "route_desc":
                  query.value("description", value);
                  break;
                case "route_type":
                  query.value("route_type", Integer.parseInt(value));
                  break;
                case "route_color":
                  query.value("color", value);
                  break;
                case "route_text_color":
                  query.value("text_color", value);
                  break;
                default:
                  System.out.println("Unrecognised column: " + column);
              }
            }
            ResultSet rs = session.execute(query);
            if (!rs.wasApplied()) {
              System.out.println("Failed to save route with id: " + route_id);
            }
          }
        }
      }
      timetable.updateDatabase(session, SYDNEY_BUSSES_UUID);
    } catch (IOException e) {
        e.printStackTrace();
        return;
    }
    System.out.println("Timetable update complete.");
  };

  private ZipInputStream fetchTimetableZip(String url) throws IOException {
    HttpURLConnection connection = (HttpURLConnection) new URL(url).openConnection();
    connection.setRequestProperty(API_KEY_HEADER_NAME, API_KEY_HEADER_CONTENTS);
    connection.connect();
    return new ZipInputStream(connection.getInputStream());
  }

  private void fetchCurrentDelays() {
    HttpURLConnection connection = null;
    try {
      System.out.println("Fetching realtime stream.");
      connection = (HttpURLConnection) new URL(BUS_REALTIME_URL).openConnection();
      connection.setRequestProperty(API_KEY_HEADER_NAME, API_KEY_HEADER_CONTENTS);
      connection.connect();

      GtfsRealtime.FeedMessage feed = GtfsRealtime.FeedMessage.parseFrom(connection.getInputStream());
      System.out.println("Fetch complete. Processing.");
      Calendar calendar = Calendar.getInstance();
      long now = calendar.getTime().getTime() / 1000 + 180; // Convert to seconds
      System.out.println(now);
      for (GtfsRealtime.FeedEntity entity : feed.getEntityList()) {
        if (entity.hasTripUpdate()) {
          GtfsRealtime.TripDescriptor trip = entity.getTripUpdate().getTrip();
          for (GtfsRealtime.TripUpdate.StopTimeUpdate stopTimeUpdate : entity.getTripUpdate().getStopTimeUpdateList()) {
            if (stopTimeUpdate.hasDeparture() && stopTimeUpdate.getDeparture().hasDelay()) {
              int delay = stopTimeUpdate.getDeparture().getDelay();
              long time = stopTimeUpdate.getDeparture().getTime();
              if (now > time) {
                if (trip.getRouteId().equals("2441_370")) {
                  System.out.println("start date: " + trip.getStartDate());
                  System.out.println("start time: " + trip.getStartTime());
                  System.out.println("trip id: " + trip.getTripId());
                  System.out.println("stop id: " + stopTimeUpdate.getStopId());
                  System.out.println("stop sequence: " + stopTimeUpdate.getStopSequence());
                  System.out.println("delay: " + stopTimeUpdate.getDeparture().getDelay());
                  System.out.println("time: " + stopTimeUpdate.getDeparture().getTime());
                  System.out.println("now: " + now);
                  System.out.println("");
                }
                if (delay > latestDelay) {
                  latestDelay = delay;
                  latestBus = trip.getRouteId();
                  latestStop = stopTimeUpdate.getStopId();
                }
              }
            }
          }
        }
      }
    } catch (IOException e) {
      e.printStackTrace();
    }
    System.out.println("Processing complete.");
  }
}
