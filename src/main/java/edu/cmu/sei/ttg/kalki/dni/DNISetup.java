package edu.cmu.sei.ttg.kalki.dni;

import edu.cmu.sei.ttg.kalki.dni.alerts.AlertServerStartup;
import edu.cmu.sei.ttg.kalki.dni.umbox.DeviceSecurityStateInsertHandler;
import edu.cmu.sei.ttg.kalki.dni.utils.Config;
import edu.cmu.sei.ttg.kalki.database.Postgres;
import edu.cmu.sei.ttg.kalki.listeners.InsertListener;

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
            DNISetup.setupDatabase();

            InsertListener.startUpListener(Postgres.TRIGGER_NOTIF_NEW_DEV_SEC_STATE, new DeviceSecurityStateInsertHandler());

            AlertServerStartup.start();
        }
        catch(Exception e)
        {
            e.printStackTrace();
        }
    }

    /**
     * Creates DB objects if needed, but also initializes the DB singleton.
     * @throws SQLException
     */
    private static void setupDatabase() throws SQLException
    {
        String rootPassword = Config.data.get("db_root_password");;
        String dbName = Config.data.get("db_name");
        String dbUser = Config.data.get("db_user");
        String dbPass = Config.data.get("db_password");
        String recreateDB = Config.data.get("db_recreate");
        String setupDB = Config.data.get("db_setup");

        if(recreateDB.equals("true"))
        {
            // Recreate DB and user.
            Postgres.removeDatabase(rootPassword, dbName);
            Postgres.removeUser(rootPassword, dbUser);
            Postgres.createUserIfNotExists(rootPassword, dbUser, dbPass);
            Postgres.createDBIfNotExists(rootPassword, dbName, dbUser);
        }

        // Make initial connection, setting up the singleton.
        Postgres.initialize(dbName, dbUser, dbPass);

        if(setupDB.equals("true"))
        {
            // Create tables, triggers, and more.
            Postgres.setupDatabase();
        }
    }
}