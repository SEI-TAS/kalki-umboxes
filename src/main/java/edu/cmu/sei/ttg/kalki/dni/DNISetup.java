package edu.cmu.sei.ttg.kalki.dni;

import edu.cmu.sei.ttg.kalki.dni.alerts.AlertServerStartup;
import edu.cmu.sei.ttg.kalki.dni.utils.Config;
import kalkidb.database.Postgres;

import java.sql.SQLException;

/**
 * Entry point for the program.
 */
public class DNISetup
{
    /**
     * Sets up the Config and Postgres singletons, starts up the AlertHandler http server.
     */
    public static void startUpComponents()
    {
        try
        {
            Config.load("config.json");

            DNISetup.setupDatabase();

            AlertServerStartup.start();
        }
        catch(Exception e)
        {
            e.printStackTrace();
        }
    }

    /**
     * Creates DB objects if needed, but also intializes the DB singleton.
     * @throws SQLException
     */
    private static void setupDatabase() throws SQLException
    {
        String rootPassword = Config.data.get("db_root_password");;
        String dbName = Config.data.get("db_name");
        String dbUser = Config.data.get("db_user");
        String dbPass = Config.data.get("db_password");
        String resetDB = Config.data.get("db_reset");

        if(resetDB.equals("true"))
        {
            // Recreate DB and user.
            Postgres.removeDatabase(rootPassword, dbName);
            Postgres.removeUser(rootPassword, dbUser);
            Postgres.createUserIfNotExists(rootPassword, dbUser, dbPass);
            Postgres.createDBIfNotExists(rootPassword, dbName, dbUser);
        }

        // Make initial connection, setting up the singleton.
        Postgres.initialize(dbName, dbUser, dbPass);

        if(resetDB.equals("true"))
        {
            // Create tables, triggers, and more.
            Postgres.setupDatabase();
        }
    }
}