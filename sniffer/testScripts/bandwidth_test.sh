#!/usr/bin/env bash

# Information configured in the auth proxy.
#DEFAULT_ADDRESS=
#DEFAULT_PORT=9010
#RIGHT_USER=kuser
#RIGHT_PASS=kpass

# Selectable Actions:
# 1: UDP_PASSTHROUGH.  This test is intended to test UDP throughput when it is passed through the data node without processing
# 2: TCP_BLOCKED.  This test is intended to test blocked TCP traffic throughput on the data node.
# 3: TCP_INVALID.  This test is intended to test invalid (but not blocked) TCP traffic throughput that is forwarded by the data node to the IoT device.
# 4: TCP_VALID.  This test is intended to test valid TCP traffic throughput that is forwarded by the data node to the IoT device.
# 5: IOT_CHECK.  This test is intended simply to periodically change the state of the IoT device in order to confirm functionality.
#    It should be run concurrently with another test to measure capability at different loads.
#    It runs for 5 minutes and executes a change every 1 seconds.

# Action and IoT device info, get from command line or use defaults.
OPTION=${1:-'IOT_CHECK'}
DEVICE_IP=${2:-'192.168.1.101'}

DEVICE_PORT=${3:-80}

hueColorValue=1000

echo "Action: ${OPTION}, IP: ${DEVICE_IP}, DEVICE PORT: ${DEVICE_PORT}"

# Disable proxy, if any.
export http_proxy='';

# Command line argument tells us what to do.
if [ "$OPTION" = "UDP_PASSTHROUGH" ]; then
    # Set bandwidth to 50Kb for 20 seconds
    echo -e "\nSetting bandwidth load to 50kbps UDP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -u -b 50k -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 100Kb for 20 seconds
    echo "Setting bandwidth load to 100kbps UDP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -u -b 100k -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 250Kb for 20 seconds
    echo "Setting bandwidth load to 250kbps UDP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -u -b 250k -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 500Kb for 20 seconds
    echo "Setting bandwidth load to 500kbps UDP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -u -b 500k -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 1Mb for 20 seconds
    echo "Setting bandwidth load to 1mbps UDP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -u -b 1m -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 5Mb for 20 seconds
    echo "Setting bandwidth load to 5mbps UDP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -u -b 5m -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 10Mb for 20 seconds
    echo "Setting bandwidth load to 10mbps UDP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -u -b 10m -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 20Mb for 20 seconds
    echo "Setting bandwidth load to 20mbps UDP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -u -b 20m -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 30Mb for 20 seconds
    echo "Setting bandwidth load to 30mbps UDP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -u -b 30m -t 20
    echo "Done."
elif [ "$OPTION" = "TCP_BLOCKED" ]; then
    # Set bandwidth to 50Kb for 20 seconds
    echo -e "\nSetting bandwidth load to 50kbps TCP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -b 50k -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 100Kb for 20 seconds
    echo "Setting bandwidth load to 100kbps TCP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -b 100k -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 250Kb for 20 seconds
    echo "Setting bandwidth load to 250kbps TCP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -b 250k -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 500Kb for 20 seconds
    echo "Setting bandwidth load to 500kbps TCP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -b 500k -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 1Mb for 20 seconds
    echo "Setting bandwidth load to 1mbps TCP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -b 1m -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 5Mb for 20 seconds
    echo "Setting bandwidth load to 5mbps TCP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -b 5m -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 10Mb for 20 seconds
    echo "Setting bandwidth load to 10mbps TCP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -b 10m -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 20Mb for 20 seconds
    echo "Setting bandwidth load to 20mbps TCP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -b 20m -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 30Mb for 20 seconds
    echo "Setting bandwidth load to 30mbps TCP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -b 30m -t 20
    echo "Done."
elif [ "$OPTION" = "TCP_INVALID" ]; then
    # Set bandwidth to 50Kb for 20 seconds
    echo -e "\nSetting bandwidth load to 50kbps TCP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -b 50k -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 100Kb for 20 seconds
    echo "Setting bandwidth load to 100kbps TCP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -b 100k -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # End here; there's no reason to increase bandwidth to a legitimate IoT device over 100Kb (for this use case)
    break

    # Set bandwidth to 250Kb for 20 seconds
    echo "Setting bandwidth load to 250kbps TCP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -b 250k -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 500Kb for 20 seconds
    echo "Setting bandwidth load to 500kbps TCP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -b 500k -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 1Mb for 20 seconds
    echo "Setting bandwidth load to 1mbps TCP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -b 1m -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 5Mb for 20 seconds
    echo "Setting bandwidth load to 5mbps TCP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -b 5m -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 10Mb for 20 seconds
    echo "Setting bandwidth load to 10mbps TCP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -b 10m -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 20Mb for 20 seconds
    echo "Setting bandwidth load to 20mbps TCP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -b 20m -t 20
    echo -e "Done.  Waiting 5 seconds.\n\n"
    sleep 5

    # Set bandwidth to 30Mb for 20 seconds
    echo "Setting bandwidth load to 30mbps TCP traffic for 20 seconds."
    iperf -c ${DEVICE_IP} -b 30m -t 20
    echo "Done."
elif [ "$OPTION" = "TCP_VALID" ]; then
    # Set bandwidth to 50Kb for 20 seconds; at 12,392 bits per Curl command, that's 12.101Kb; for 50Kb, do this 5x per sec
    let hueColorValue=1000
    echo -e "Sending hue color to IoT device at $DEVICE_IP:$DEVICE_PORT at a 60.5Kbps rate for 20 sec"
    for i in {1..20}
    do
        for i in {1..5}
        do
             # Send a command to the device to change the light value
             curl -d "{'hue': $hueColorValue}" -X PUT http://${DEVICE_IP}:${DEVICE_PORT}/api/newdeveloper/lights/1/state > /dev/null 2>&1

             # Increment Hue Color Value
             let hueColorValue=$hueColorValue+320

             # Wait .1 seconds to next send to not overwhelm each burst
             #sleep .1
        done
        # Wait until a full second is over, assuming near-instant execution time on each send, so 1 - (.1 * 5) = .5
        sleep 1
    done

    # Wait 2 sec to let the network settle
    echo "Done; Sleeping 2 sec"
    sleep 2

    # Set bandwidth to 100Kb for 20 seconds; at 12,392 bits per Curl command, that's 12.101Kb; for 100Kb, do this 9x per sec
    let hueColorValue=1000
    echo -e "Sending hue color to IoT device at $DEVICE_IP:$DEVICE_PORT at a 108.9Kbps rate for 20 sec"
    for i in {1..20}
    do
        for i in {1..9}
        do
             # Send a command to the device to change the light value
             curl -d "{'hue': $hueColorValue}" -X PUT http://${DEVICE_IP}:${DEVICE_PORT}/api/newdeveloper/lights/1/state > /dev/null 2>&1

             # Increment Hue Color Value
             let hueColorValue=$hueColorValue+160

             # Wait .05 seconds to next send to not overwhelm each burst
             #sleep .05
        done
        # Wait until a full second is over, assuming near-instant execution time on each send, so 1 - (.05 * 9) = .55
        sleep 1
    done

    # Wait 2 sec to let the network settle
    echo "Done; Sleeping 2 sec"
    sleep 2

    # Set bandwidth to 250Kb for 20 seconds; at 12,392 bits per Curl command, that's 12.101Kb; for 250Kb, do this 21x per sec
    let hueColorValue=1000
    echo -e "Sending hue color to IoT device at $DEVICE_IP:$DEVICE_PORT at a 254.1Kbps rate for 20 sec"
    for i in {1..20}
    do
        for i in {1..21}
        do
             # Send a command to the device to change the light value
             curl -d "{'hue': $hueColorValue}" -X PUT http://${DEVICE_IP}:${DEVICE_PORT}/api/newdeveloper/lights/1/state > /dev/null 2>&1

             # Increment Hue Color Value
             let hueColorValue=$hueColorValue+80

             # Wait .02 seconds to next send to not overwhelm each burst
             #sleep .02
        done
        # Wait until a full second is over, assuming near-instant execution time on each send, so 1 - (.02 * 21) = .58
        sleep 1
    done

    # Wait 2 sec to let the network settle
    echo "Done; Sleeping 2 sec"
    sleep 2

    # Set bandwidth to 500Kb for 20 seconds; at 12,392 bits per Curl command, that's 12.101Kb; for 500Kb, do this 42x per sec
    let hueColorValue=1000
    echo -e "Sending hue color to IoT device at $DEVICE_IP:$DEVICE_PORT at a 508.24Kbps rate for 20 sec"
    for i in {1..20}
    do
        for i in {1..42}
        do
             # Send a command to the device to change the light value
             curl -d "{'hue': $hueColorValue}" -X PUT http://${DEVICE_IP}:${DEVICE_PORT}/api/newdeveloper/lights/1/state > /dev/null 2>&1

             # Increment Hue Color Value
             let hueColorValue=$hueColorValue+40

             # Wait .01 seconds to next send to not overwhelm each burst
             #sleep .01
        done
        # Wait until a full second is over, assuming near-instant execution time on each send, so 1 - (.01 * 42) = .58
        sleep 1
    done

    # Wait 2 sec to let the network settle
    echo "Done; Sleeping 2 sec"
    sleep 2

    # Set bandwidth to 1Mb for 20 seconds; at 12,392 bits per Curl command, that's 12.101Kb; for 1Mb, do this 85x per sec
    let hueColorValue=1000
    echo -e "Sending hue color to IoT device at $DEVICE_IP:$DEVICE_PORT at a 1.004Mbps rate for 20 sec"
    for i in {1..20}
    do
        for i in {1..85}
        do
             # Send a command to the device to change the light value
             curl -d "{'hue': $hueColorValue}" -X PUT http://${DEVICE_IP}:${DEVICE_PORT}/api/newdeveloper/lights/1/state > /dev/null 2>&1

             # Increment Hue Color Value
             let hueColorValue=$hueColorValue+20

             # Wait .01 seconds to next send to not overwhelm each burst
             #sleep .01
        done
        # Wait until a full second is over, assuming near-instant execution time on each send, so 1 - (.01 * 85) = .15
        sleep 1
    done

    echo "Done."
    # Set bandwidth to 5Mb for 20 seconds


    # Set bandwidth to 10Mb for 20 seconds


    # Set bandwidth to 20Mb for 20 seconds


    # Set bandwidth to 30Mb for 20 seconds
elif [ "$OPTION" = "IOT_CHECK" ]; then
    # Loop for 5 minutes, executing every 1 seconds; e.g. 300 iterations
    for i in {1..300}
    do
        # Send a command to the device to change the light value
        echo -e "Sending hue color $hueColorValue to IoT device at $DEVICE_IP:$DEVICE_PORT."
        curl -d "{'hue': $hueColorValue}" -X PUT http://${DEVICE_IP}:${DEVICE_PORT}/api/newdeveloper/lights/1/state
        #curl -d "{\"hue\": $hueColorValue}" -X PUT http://${DEVICE_IP}:${DEVICE_PORT}/api/newdeveloper/lights/1/state
        echo -e "\n"

        # Increment Hue Color Value
        let hueColorValue=$hueColorValue+100

        # Wait 1 seconds to next send
        sleep 1
    done
else
    echo "Invalid option selected: ${OPTION}"
fi
