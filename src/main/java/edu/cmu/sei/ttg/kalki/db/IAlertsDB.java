package edu.cmu.sei.ttg.kalki.db;

public interface IAlertsDB
{
    void storeAlert(String umboxId, String alertText);
}
