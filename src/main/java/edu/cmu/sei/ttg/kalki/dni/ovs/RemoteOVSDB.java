package edu.cmu.sei.ttg.kalki.dni.ovs;

import edu.cmu.sei.ttg.kalki.dni.utils.CommandExecutor;

import java.text.MessageFormat;
import java.util.ArrayList;
import java.util.List;

/***
 * Represents a remove OVS DB. Communicates to it through OpenFlow using the ovs-vsctl local command line
 * tool.
 */
public class RemoteOVSDB
{
    // TODO: how to handle sudo permissions needed for this command?
    private static final String TOOL_COMMAND = "sudo ovs-vsctl";
    private static final String SERVER_PARAM = "--db=tcp:{0}:{1}";
    private static final String GET_PORT_COMMAND = "get Interface {0} ofport";

    private static final int DEFAULT_PORT = 6654;

    private String serverIp;
    private int port;

    public RemoteOVSDB(String serverIP)
    {
        this(serverIP, DEFAULT_PORT);
    }

    public RemoteOVSDB(String serverIP, int port)
    {
        this.serverIp = serverIP;
        this.port = port;
    }

    /***
     * Gets the numeric id of a port given the port's name.
     */
    public String getPortId(String portName)
    {
        List<String> output = sendCommand(MessageFormat.format(GET_PORT_COMMAND, portName), new ArrayList<>());
        return output.get(0);
    }

    /***
     * Sends a generic command to a remote OVS DB through the local command line tool.
     */
    private List<String> sendCommand(String command, List<String> arguments)
    {
        List<String> commandInfo = new ArrayList<>();
        commandInfo.add(TOOL_COMMAND);
        commandInfo.add(MessageFormat.format(SERVER_PARAM, serverIp, port));
        commandInfo.add(command);
        commandInfo.addAll(arguments);

        List<String> output = CommandExecutor.executeCommand(commandInfo);
        return output;
    }
}
