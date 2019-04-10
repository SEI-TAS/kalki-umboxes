package edu.cmu.sei.ttg.kalki;

import edu.cmu.sei.ttg.kalki.db.SQLAlertDB;
import kalkidb.database.Postgres;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.servlet.ServletContextHandler;

/**
 * Entry point for the program.
 */
public class Program
{
    private static final String ALERT_URL = "/alert";
    private static final int SERVER_PORT = 6060;

    private static final String DB_NAME = "kalkidb";
    private static final String DB_USER = "kalkiuser";
    private static final String DB_PWD = "kalkipass";

    /**
     * Simply starts a Jetty server, with a handler for new alert notifications.
     * @param args
     */
    public static void main(String[] args)
    {
        try
        {
            // Just to ensure DB is created and ready.
            String rootPassword = "postgres";
            //Postgres.removeDatabase(rootPassword, DB_NAME);
            //Postgres.removeUser(rootPassword, DB_USER);
            Postgres.createUserIfNotExists(rootPassword, DB_USER, DB_PWD);
            boolean dbCreated = Postgres.createDBIfNotExists(rootPassword, DB_NAME, DB_USER);
            Postgres.initialize(DB_NAME, DB_USER, DB_PWD);
            if(dbCreated)
            {
                Postgres.setupDatabase();
            }

            Server server = new Server(SERVER_PORT);
            ServletContextHandler handler = new ServletContextHandler(server, ALERT_URL);
            handler.addServlet(AlertHandlerServlet.class, "/");
            server.start();
        }
        catch(Exception e)
        {
            e.printStackTrace();
        }
    }

}