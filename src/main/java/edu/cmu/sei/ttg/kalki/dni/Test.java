package edu.cmu.sei.ttg.kalki.dni;

import edu.cmu.sei.ttg.kalki.dni.umbox.Umbox;
import kalkidb.database.Postgres;
import kalkidb.models.Device;
import kalkidb.models.Group;
import kalkidb.models.UmboxImage;

/***
 * Simple class for quick tests.
 */
public class Test
{
    private static int testDeviceId = -1;
    private static String testImageName = "umbox-sniffer";

    /**
     * Entry point for the program.
     */
    public static void main(String[] args)
    {
        try
        {
            DNISetup.startUpComponents();

            String resetDB = Config.data.get("db_reset");
            if(resetDB.equals("true"))
            {
                insertTestData();
                // TODO: Sleep or wait for dev id to be inserted?
            }

            runSimpleTest();
        }
        catch(Exception e)
        {
            e.printStackTrace();
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
            Postgres.insertDevice(newDevice).whenComplete((deviceId, devException) -> {
                testDeviceId = deviceId;
            });
        });

        UmboxImage image = new UmboxImage("umbox-sniffer", "/home/kalki/images/umbox-sniffer.qcow2");
        Postgres.insertUmboxImage(image).whenComplete((umboxImageId, exception) -> {
            testUmboxImageId = umboxImageId;
        });
    }

    /***
     * Simple test to try out starting and directing traffic to a umbox.
     */
    private static void runSimpleTest()
    {
        Umbox.startDeviceUmbox(testImageName, testDeviceId);
    }
}
