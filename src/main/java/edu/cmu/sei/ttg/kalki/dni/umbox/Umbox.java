package edu.cmu.sei.ttg.kalki.dni.umbox;

import edu.cmu.sei.ttg.kalki.dni.utils.CommandExecutor;
import edu.cmu.sei.ttg.kalki.dni.utils.Config;
import kalkidb.database.Postgres;
import kalkidb.models.Device;
import kalkidb.models.UmboxImage;
import kalkidb.models.UmboxInstance;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class Umbox
{
    private static final int MAX_INSTANCES = 1000;

    private int umboxId;
    private Device device;
    private UmboxImage image;

    private ArrayList<String> commandInfo;

    /***
     * Constructor for new umboxes.
     * @param device
     * @param image
     */
    public Umbox(UmboxImage image, Device device)
    {
        this.image = image;
        this.device = device;

        // Generate random id.
        Random rand = new Random();
        umboxId = rand.nextInt(MAX_INSTANCES);

        setupCommand();
    }

    /***
     * Constructor for existing umboxes.
     * @param instanceId
     */
    public Umbox(UmboxImage image, int instanceId)
    {
        this.image = image;
        this.device = null;
        this.umboxId = instanceId;

        setupCommand();
    }

    /***
     * Common parameters that are the same (needed or optional) for all comands.
     */
    private void setupCommand()
    {
        String dataNodeIP = Config.data.get("data_node_ip");
        String ovsDataBridge = Config.data.get("ovs_data_bridge");
        String controlBridge = Config.data.get("control_bridge");
        String umboxToolPath = Config.data.get("umbox_tool_path");

        // Basic command parameters.
        commandInfo = new ArrayList<>();
        commandInfo.add("python");
        commandInfo.add(umboxToolPath);
        commandInfo.add("-s");
        commandInfo.add(dataNodeIP);
        commandInfo.add("-u");
        commandInfo.add(String.valueOf(umboxId));
        commandInfo.add("-i");
        commandInfo.add(image.getName());
        commandInfo.add("-p");
        commandInfo.add(image.getPath());
        commandInfo.add("-bc");
        commandInfo.add(controlBridge);
        commandInfo.add("-bd");
        commandInfo.add(ovsDataBridge);
    }

    /**
     * Starts a new umbox.
     * @returns the name of the OVS port the umbox was connected to.
     */
    public String start()
    {
        List<String> command = (ArrayList) commandInfo.clone();
        command.add("-c");
        command.add("start");

        try
        {
            List<String> output = CommandExecutor.executeCommand(command);

            // Store in the DB the information about the newly created umbox instance.
            UmboxInstance instance = new UmboxInstance(String.valueOf(umboxId), image.getId(), device.getId());
            instance.insert();

            String portName = output.get(output.size() - 1);
            System.out.println("Umbox port name: " + portName);
            return portName;
        }
        catch (RuntimeException e)
        {
            e.printStackTrace();
        }

        return null;
    }

    /**
     * Stops a running umbox.
     */
    public void stop()
    {
        List<String> command = (ArrayList) commandInfo.clone();
        command.add("-c");
        command.add("stop");

        try
        {
            CommandExecutor.executeCommand(command);

            Postgres.findUmboxInstance(String.valueOf(umboxId)).whenComplete((umboxInstance, exception) ->
            {
                // TODO: Keep instance marked as off, instead of deleting it.
                Postgres.deleteUmboxInstance(umboxInstance.getId());
            });
        }
        catch (RuntimeException e)
        {
            e.printStackTrace();
        }
    }

}
