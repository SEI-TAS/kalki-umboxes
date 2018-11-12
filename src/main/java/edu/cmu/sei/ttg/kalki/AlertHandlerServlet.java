package edu.cmu.sei.ttg.kalki;

import java.io.BufferedReader;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import kalkidb.database.Postgres;
import kalkidb.models.AlertHistory;
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
            throws ServletException
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
            String alerterId = alertData.getString("alerter");
            String alertText = alertData.getString("alert");

            // Store info in DB
            System.out.println("alerterId: " + alerterId);
            System.out.println("alert: " + alertText);
            AlertHistory alertHistory = new AlertHistory();
            alertHistory.setAlerterId(alerterId);
            alertHistory.setInfo(alertText);
            Postgres.insertAlertHistory(alertHistory);
        }
        catch (JSONException e)
        {
            throw new ServletException("Error parsing JSON request string: " + e.toString());
        }

        response.setStatus(HttpStatus.OK_200);
    }
}
