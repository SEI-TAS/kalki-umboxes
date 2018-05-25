package edu.cmu.sei.ttg.kalki;

import edu.cmu.sei.ttg.kalki.db.SQLAlertDB;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.servlet.ServletContextHandler;

/**
 * Entry point for the program.
 */
public class Program
{
    private static final String ALERT_URL = "/alert";
    private static final int SERVER_PORT = 6060;

    /**
     * Simply starts a Jetty server, with a handler for new alert notifications.
     * @param args
     */
    public static void main(String[] args)
    {
        try
        {
            // Just to ensure DB is created and ready.
            SQLAlertDB.getInstance("");

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