package edu.cmu.sei.ttg.kalki.dni;

import edu.cmu.sei.ttg.kalki.dni.alerts.AlertServerStartup;
import kalkidb.database.Postgres;
import kalkidb.models.Device;
import kalkidb.models.Group;

import java.sql.SQLException;

/**
 * Entry point for the program.
 */
public class Program
{
    /**
     * Simply starts a Jetty server, with a handler for new alert notifications.
     * @param args
     */
    public static void main(String[] args)
    {
        try
        {
            Config.load("config.json");

            Program.setupDatabase();

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

            // Inserts basic data for testing.
            insertTestData();
        }
    }

    /***
     * Inserts default data to run simple tests.
     */
    private static void insertTestData()
    {
        Group newGroup = new Group("testGroup");
        Postgres.insertGroup(newGroup).whenComplete((groupId, exception) -> {
            int defaultType = 1;
            String deviceIp = "192.168.56.103";
            Device newDevice = new Device("testDevice", "test device", defaultType, groupId, deviceIp, 10, 10);
            Postgres.insertDevice(newDevice);
        });
    }

}