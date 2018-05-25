package edu.cmu.sei.ttg.kalki.db;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class FileAlertDB implements IAlertsDB
{
    private static final String DEFAULT_FILE_PATH = "state.json";

    private static FileAlertDB instance = null;

    private Map<Long, AlertInfo> alerts = new HashMap<>();
    private String filePath;

    protected FileAlertDB() throws IOException
    {
        this.filePath = DEFAULT_FILE_PATH;
        loadFromFile();
    }

    public static FileAlertDB getInstance() throws IOException
    {
        if(instance == null)
        {
            instance = new FileAlertDB();
        }
        return instance;
    }

    private void loadFromFile() throws IOException
    {
        FileInputStream fileInputStream;
        try
        {
            fileInputStream = new FileInputStream(filePath);
        }
        catch(IOException ex)
        {
            System.out.println("State file " + filePath + " not found, will be created.");
            return;
        }

        // Load the whole data contents and parse them as JSON.
        int fileLength = (int) (new File(filePath)).length();
        byte[] data = new byte[fileLength];
        fileInputStream.read(data);
        fileInputStream.close();
        String jsonString = new String(data);
        JSONObject json = new JSONObject(jsonString);

        // Load all tokens/rs from json data.
        alerts.clear();
        JSONArray alertsArray = json.getJSONArray("alerts");
        for(Object alert : alertsArray)
        {
            AlertInfo alertInfo = new AlertInfo((JSONObject) alert);
            alerts.put(alertInfo.date, alertInfo);
        }
    }

    public boolean storeToFile()
    {
        try
        {
            JSONObject alertsObject = new JSONObject();
            JSONArray alertsArray = new JSONArray();
            alertsObject.put("alerts", alertsArray);
            for(long id : alerts.keySet())
            {
                AlertInfo alertInfo = alerts.get(id);
                alertsArray.put(alertInfo.toJSON());
            }

            FileWriter file = new FileWriter(filePath, false);
            file.write(alertsObject.toString());
            file.flush();
            file.close();

            return true;
        }
        catch(Exception ex)
        {
            System.out.println("Error storing alerts: " + ex.toString());
            return false;
        }
    }

    public void storeAlert(String umboxId, String alertText)
    {
        long alertTime = System.currentTimeMillis();
        AlertInfo alertInfo = new AlertInfo(umboxId, alertText, alertTime);
        alerts.put(alertTime, alertInfo);
        storeToFile();
    }
}
