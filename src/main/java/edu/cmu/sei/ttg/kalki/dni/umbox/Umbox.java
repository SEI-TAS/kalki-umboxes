package edu.cmu.sei.ttg.kalki.dni.umbox;

import kalkidb.database.Postgres;

public class UmboxManager
{
    public static void startDeviceUmbox(String umboxImageName, int deviceId)
    {
        Postgres.findDevice(deviceId).whenComplete((dev, exception) -> {
            String deviceIP = dev.getIp();
            // command(startUmboxAndRedirect);
        });
    }

    public static void stopDeviceUmbox(String umboxInstanceName)
    {
        // command(stopUmbox);
    }
}
