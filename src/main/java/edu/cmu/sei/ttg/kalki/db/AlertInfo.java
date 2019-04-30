package edu.cmu.sei.ttg.kalki.db;

import org.json.JSONObject;

public class AlertInfo
{
    public String umbox;
    public String text;
    public long date;

    public AlertInfo(String umbox, String text, long date)
    {
        this.umbox = umbox;
        this.text = text;
        this.date = date;
    }

    public AlertInfo(JSONObject jsonData)
    {
        this.umbox = jsonData.getString("umbox");
        this.text = jsonData.getString("text");
        this.date = jsonData.getLong("date");
    }

    public JSONObject toJSON()
    {
        JSONObject jsonData = new JSONObject();
        jsonData.put("umbox", umbox);
        jsonData.put("text", text);
        jsonData.put("date", date);
        return jsonData;
    }

}
