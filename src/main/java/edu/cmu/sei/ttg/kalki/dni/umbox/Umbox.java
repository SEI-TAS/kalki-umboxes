package edu.cmu.sei.ttg.kalki.dni.umbox;

import edu.cmu.sei.ttg.kalki.dni.Config;
import kalkidb.models.Device;
import kalkidb.models.UmboxImage;
import kalkidb.models.UmboxInstance;

import java.util.Random;

public class Umbox
{
    private static final int MAX_INSTANCES = 1000;

    private String dataNodeIP;
    private String ovsDataBridge;
    private String controlBridge;

    private int umboxId;
    private Device device;
    private UmboxImage image;
    private UmboxInstance instance;

    /***
     * Constructor for new umboxes.
     * @param device
     * @param image
     */
    public Umbox(Device device, UmboxImage image)
    {
        this.device = device;
        this.image = image;
        this.dataNodeIP = Config.data.get("data_node_ip");
        this.ovsDataBridge = Config.data.get("ovs_data_bridge");
        this.controlBridge = Config.data.get("control_bridge");

        // Generate random id.
        Random rand = new Random();
        umboxId = rand.nextInt(MAX_INSTANCES);
    }

    /***
     * Constructor for existing umboxes.
     * @param instanceId
     */
    public Umbox(int instanceId)
    {
        this.umboxId = instanceId;
        this.dataNodeIP = Config.data.get("data_node_ip");
    }

    /**
     * Starts a new umbox.
     */
    public void start()
    {

        sendStartUmboxCommand();

        // Store in the DB the information about the newly created umbox instance.
        instance = new UmboxInstance(String.valueOf(umboxId), image.getId(), device.getId());
        instance.insert();
    }

    /**
     * Stops a running umbox.
     */
    public void stop()
    {
        // command(stopUmbox instanceName);
        // TODO: mark instance as stopped in DB, or delete it.
    }

    private String sendStartUmboxCommand()
    {
        // execute(python umbox.py -c start -s dataNodeIP -i image.getPath(), instanceName, dataNICName, controlNICName, dataMACAddress, controlMACAddresss);
        // get (alerterId, ifaceName)
    }
}
