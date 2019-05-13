package edu.cmu.sei.ttg.kalki.dni.umbox;

import edu.cmu.sei.ttg.kalki.dni.ovs.OpenFlowRule;
import edu.cmu.sei.ttg.kalki.dni.ovs.RemoteOVSDB;
import edu.cmu.sei.ttg.kalki.dni.ovs.RemoteOVSSwitch;
import edu.cmu.sei.ttg.kalki.dni.utils.Config;
import kalkidb.database.Postgres;
import kalkidb.models.Device;
import kalkidb.models.UmboxImage;

public class DAGManager
{
    /**
     * Starts an umbox with the given image and device, and redirects traffic to/from that device to it.
     * @param image
     * @param device
     */
    public static void startAndRedirectToUmbox(UmboxImage image, Device device)
    {
        Umbox umbox = new Umbox(image, device);
        System.out.println("Starting Umbox.");
        String portName = umbox.start();

        RemoteOVSDB ovsdb = new RemoteOVSDB(Config.data.get("data_node_ip"));
        String umboxPortId = ovsdb.getPortId(portName);
        if(umboxPortId != null)
        {
            redirectToUmbox(device.getIp(), Config.data.get("ovs_devices_network_port"), umboxPortId, Config.data.get("ovs_external_network_port"));
        }
    }

    /**
     * Stops a given umbox and clears rules directing traffic to it.
     * @param image
     * @param umboxId
     */
    public static void stopAndClearRedirection(UmboxImage image, int umboxId)
    {
        Postgres.findUmboxInstance(String.valueOf(umboxId)).whenComplete((instance, exception) ->
        {
            Postgres.findDevice(instance.getDeviceId()).whenComplete((device, exceptionDev) ->
            {
                clearRedirectToUmbox(device.getIp());

                Umbox umbox = new Umbox(image, umboxId);
                System.out.println("Stopping umbox.");
                umbox.stop();
            });
        });
    }

    /**
     * Sends all OpenFlow rules needed to redirect traffic from and to a device to a given umbox.
     * @param deviceIp
     * @param ovsDevicePort
     * @param ovsUmboxPort
     * @param ovsExternalPort
     */
    private static void redirectToUmbox(String deviceIp, String ovsDevicePort, String ovsUmboxPort, String ovsExternalPort)
    {
        OpenFlowRule extToUmbox = new OpenFlowRule(ovsExternalPort, ovsUmboxPort, "100", null, deviceIp);
        OpenFlowRule umboxToDev = new OpenFlowRule(ovsUmboxPort, ovsDevicePort, "110", null, deviceIp);
        OpenFlowRule devToUmbox = new OpenFlowRule(ovsDevicePort, ovsUmboxPort, "100", deviceIp, null);
        OpenFlowRule umboxToExt = new OpenFlowRule(ovsUmboxPort, ovsExternalPort, "110", deviceIp, null);

        RemoteOVSSwitch vSwitch = new RemoteOVSSwitch(Config.data.get("data_node_ip"));
        vSwitch.addRule(extToUmbox);
        vSwitch.addRule(umboxToDev);
        vSwitch.addRule(devToUmbox);
        vSwitch.addRule(umboxToExt);
    }

    /**
     * Clears all rules related to incoming and outgoing traffic for a given device.
     * @param deviceIp
     */
    private static void clearRedirectToUmbox(String deviceIp)
    {
        OpenFlowRule allFromDevice = new OpenFlowRule(null, null, null, deviceIp, null);
        OpenFlowRule allToDevice = new OpenFlowRule(null, null, null, null, deviceIp);

        RemoteOVSSwitch vSwitch = new RemoteOVSSwitch(Config.data.get("data_node_ip"));
        vSwitch.addRule(allFromDevice);
        vSwitch.addRule(allToDevice);
    }
}