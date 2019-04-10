package edu.cmu.sei.ttg.kalki.db;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Properties;

public class SQLAlertDB implements IAlertsDB
{
    // The default root-user name.
    private static final String ROOT_USER = "postgres";

    // The default database name.
    private static final String BASE_DB = "postgres";

    // The default connection URL for the database.
    private static final String DEFAULT_DB_URL = "jdbc:postgresql://localhost:5432";

    // The default db name, user and password.
    private static final String DEFAULT_USER = "kalkiuser";
    private static final String DEFAULT_PWD = "kalkipass";
    private static final String DEFAULT_DB_NAME = "kalkidb";

    // The singleton instance.
    private static SQLAlertDB instance = null;

    protected SQLAlertDB(String rootPwd) throws SQLException
    {
        createUserIfNotExists(rootPwd, DEFAULT_USER, DEFAULT_PWD);
        createDBAndTablesIfNotExist(rootPwd, DEFAULT_DB_NAME, DEFAULT_USER);
    }

    public static SQLAlertDB getInstance(String rootPwd) throws SQLException
    {
        if(instance == null)
        {
            instance = new SQLAlertDB(rootPwd);
        }
        return instance;
    }

    @Override
    public void storeAlert(String umboxId, String alertText)
    {
        try (Connection conn = getDBConnection())
        {
            PreparedStatement insertAlert = conn.prepareStatement("INSERT INTO alert_history (umbox_external_id, info) VALUES (?,?);");
            insertAlert.setString(1, umboxId);
            insertAlert.setString(2, alertText);
            insertAlert.execute();
        }
        catch (SQLException e)
        {
            e.printStackTrace();
            throw new RuntimeException("Error storing alert: " + e.toString());
        }
    }

    private Connection getRootConnection(String rootPwd) throws SQLException
    {
        Properties connectionProps = new Properties();
        connectionProps.put("user", ROOT_USER);
        connectionProps.put("password", rootPwd);
        return DriverManager.getConnection(DEFAULT_DB_URL + "/" + BASE_DB, connectionProps);
    }

    private Connection getDBConnection() throws SQLException {
        Properties connectionProps = new Properties();
        connectionProps.put("user", DEFAULT_USER);
        connectionProps.put("password", DEFAULT_PWD);
        return DriverManager.getConnection(DEFAULT_DB_URL + "/" + DEFAULT_DB_NAME, connectionProps);
    }

    public synchronized void createUserIfNotExists(String rootPwd, String user, String password) throws SQLException {
        String createUser = "DO\n" +
                "$body$\n" +
                "BEGIN\n" +
                "   IF NOT EXISTS (\n" +
                "      SELECT *\n" +
                "      FROM   pg_catalog.pg_user\n" +
                "      WHERE  usename = '" +  user + "') THEN\n" +
                "\n" +
                "      CREATE ROLE " +  user + " LOGIN PASSWORD '"
                +  password + "';\n" +
                "   END IF;\n" +
                "END\n" +
                "$body$;";

        try (Connection rootConn = getRootConnection(rootPwd);
             Statement stmt = rootConn.createStatement())
        {
            stmt.execute(createUser);
        }
        catch (SQLException e) {
            e.printStackTrace();
            throw e;
        }
    }

    public synchronized void createDBAndTablesIfNotExist(String rootPwd, String dbName, String dbUser) throws SQLException {
        // First check it DB exists.
        String checkDB = "SELECT datname FROM pg_catalog.pg_database "
                + "WHERE datname = '" + dbName + "';";
        try (Connection rootConn = getRootConnection(rootPwd);
             Statement stmt = rootConn.createStatement();
             ResultSet result = stmt.executeQuery(checkDB))
        {
            if (result.next())
            {
                // Treat this as a "create if not exist", so if it exists, end method without doing anything.
                return;
            }
        }
        catch (SQLException e) {
            e.printStackTrace();
            throw e;
        }

        // Create the database.
        String createDB = "CREATE DATABASE " + dbName
                + " WITH OWNER= " + dbUser
                + " ENCODING = 'UTF8' TEMPLATE = template0 "
                + " CONNECTION LIMIT = -1;";
        try (Connection rootConn = getRootConnection(rootPwd);
             Statement stmt = rootConn.createStatement())
        {
            stmt.execute(createDB);
        } catch (SQLException e) {
            e.printStackTrace();
            throw e;
        }

        String alertTableSQL = "CREATE TABLE alert_history ("
                + "id serial PRIMARY KEY, "
                + "umbox_external_id varchar(255) NOT NULL, "
                + "info varchar(255) NOT NULL, "
                + "stamp bigint NOT NULL "
                + ");";

        String umboxTableSQL = "CREATE TABLE umbox_instance ("
                + "id serial PRIMARY KEY, "
                + "umbox_external_id varchar(255) NOT NULL, "
                + "device_id varchar(255) NOT NULL, "
                + "started_at bigint NOT NULL "
                + ");";

        // Table creation in PostgreSQL needs to be done with a connection
        // using the local user and not the root user, so that the local
        // user will be automatically set as the owner of the tables.
        try (Connection rootConn = getDBConnection();
             Statement stmt = rootConn.createStatement())
        {
            stmt.execute(alertTableSQL);
            stmt.execute(umboxTableSQL);
        } catch (SQLException e) {
            e.printStackTrace();
            throw e;
        }
    }

}
