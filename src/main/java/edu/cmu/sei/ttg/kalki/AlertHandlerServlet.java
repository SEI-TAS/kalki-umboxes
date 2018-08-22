package edu.cmu.sei.ttg.kalki;

import java.io.BufferedReader;
import java.io.IOException;
import java.sql.SQLException;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import edu.cmu.sei.ttg.kalki.db.FileAlertDB;
import edu.cmu.sei.ttg.kalki.db.SQLAlertDB;
import org.eclipse.jetty.http.HttpStatus;

import org.json.JSONException;
import org.json.JSONObject;

/**
 * Servlet that handles a new alert and stores it for the controller to use.
 */
public class AlertHandlerServlet extends HttpServlet
{
    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException
    {
        // Parse the JSON data from the alert.
        JSONObject alertData;
        try
        {
            String bodyLine;
            StringBuilder jsonBody = new StringBuilder();
            BufferedReader bodyReader = request.getReader();
            while ((bodyLine = bodyReader.readLine()) != null)
            {
                jsonBody.append(bodyLine);
            }

            alertData = new JSONObject(jsonBody.toString());
        }
        catch (JSONException e)
        {
            throw new ServletException("Error parsing JSON request string");
        }
        catch (Exception e)
        {
            throw new ServletException("Error parsing request: " + e.toString());
        }

        // Store the alert data.
        try
        {
            // Get information about the alert.
            String umboxName = alertData.getString("umbox");
            String alertText = alertData.getString("alert");

            // Store info in DB
            System.out.println("umbox: " + umboxName);
            System.out.println("alert: " + alertText);
            SQLAlertDB.getInstance("").storeAlert(umboxName, alertText);

        }
        catch (JSONException e)
        {
            throw new ServletException("Error parsing JSON request string: " + e.toString());
        }
        catch (SQLException e)
        {
            throw new ServletException("Error storing alert: " + e.toString());
        }

        response.setStatus(HttpStatus.OK_200);
    }
}
