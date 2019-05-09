package edu.cmu.sei.ttg.kalki.dni;

import edu.cmu.sei.ttg.kalki.dni.umbox.Umbox;
import edu.cmu.sei.ttg.kalki.dni.utils.Config;
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
    private static int testUmboxImageId = -1;

    private static final String TEST_IMAGE_NAME = "umbox-sniffer";
    private static final String TEST_IMAGE_PATH = "/home/kalki/images/umbox-sniffer.qcow2";

    /**
     * Entry point for the program.
     */
    public static void main(String[] args)
    {
        try
        {
            Config.data.put("db_reset", "true");
            Config.data.put("db_name", "kalkidb_test");
            Config.data.put("db_user", "kalkiuser_test");

            DNISetup.startUpComponents();

            insertTestData();

            // Wait for data to be inserted.
            while(testUmboxImageId == -1)
            {
                Thread.sleep(100);
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

        UmboxImage image = new UmboxImage(TEST_IMAGE_NAME, TEST_IMAGE_PATH);
        Postgres.insertUmboxImage(image).whenComplete((umboxImageId, exception) -> {
            testUmboxImageId = umboxImageId;
        });
    }

    /***
     * Simple test to try out starting and directing traffic to a umbox.
     */
    private static void runSimpleTest()
    {
        Postgres.findDevice(testDeviceId).whenComplete((device, exception) ->
        {
            Postgres.findUmboxImage(testUmboxImageId).whenComplete((image, imageExc) ->
            {
                Umbox umbox = new Umbox(image, device);
                System.out.println("Starting VM.");
                umbox.start();

                int sleepInSeconds = 20;
                try
                {
                    Thread.sleep(sleepInSeconds * 1000);
                }
                catch (InterruptedException e)
                {
                    e.printStackTrace();
                }

                System.out.println("Stopping VM");
                umbox.stop();
            });
        });
    }
}
