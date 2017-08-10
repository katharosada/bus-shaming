package net.katiebell.busshaming.fetcher;

import com.datastax.driver.core.Cluster;
import com.datastax.driver.core.Session;

/**
 * Created by katharos on 14/05/2017.
 */
public class Cassandra {
  private static Cluster cluster = Cluster.builder().addContactPoint("127.0.0.1").build();
  private static Session session = cluster.connect();

  public static Session getSession() {
    return session;
  }
}
