package net.katiebell.busshaming.fetcher;

import com.datastax.driver.core.Session;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.ArrayList;
import java.util.List;

/**
 * Created by katharos on 17/04/2017.
 */
@Controller
public class FetchController {


  @RequestMapping("/greeting")
  public String greeting(@RequestParam(value="name", required=false, defaultValue="World") String name, Model model) {
    model.addAttribute("name", name);
    return "greeting";
  }

  @RequestMapping("/fetch")
  public String fetch(Model model) {
    model.addAttribute("latestRoute", Fetcher.latestBus);
    model.addAttribute("latestStop", Fetcher.latestStop);
    model.addAttribute("latestDelay", Fetcher.latestDelay);
    return "fetch";
  }

  @RequestMapping("/timetable")
  public String timetable(@RequestParam(value="route_id", required=false, defaultValue="370") String routeId, Model model) {
    Session session = Cassandra.getSession();
    List<Trip> tripList = Trip.fetchTripsForRoute(session, Fetcher.SYDNEY_BUSSES_UUID, routeId);
    model.addAttribute("trips", tripList);
    return "timetable";
  }

}
