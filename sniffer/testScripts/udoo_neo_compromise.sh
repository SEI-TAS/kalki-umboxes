#!/usr/bin/env bash
# USAGE
# In order to trigger the compromise alert, a total number of packets must be sent from an address within the configured
# IoT subnet that meets the configured compromise threshold (currently set to 5)

# PARAMETER OPTIONS
# -s is source IP, which is where the packet should come from; should be set to the IP of the simulated IoT device,
# which must be within the configured IoT subnet (currently set to 10.27.151); default is 10.27.151.5
# -d is destination IP, which is where the packet is addressed to go; should be set to the address of the sniffer so
# that it is received and processed; default is 127.0.0.1
# -u is udp packets, which is the number of UDP packets that will be sent from that address; default is 5
# -t is tcp packets, which is the number of TCP packets that will be sent from that address; default is 0
# -p is tcp port, which is the port at which TCP packets will be sent from; default is 31

usage()
{
  echo "Udoo Neo Compromise Script: Parameter Options"
  echo "-s is source IP, which is where the packet should come from; should be set to the IP of the simulated IoT device, which must be within the configured IoT subnet (currently set to 10.27.151); default is 10.27.151.5"
  echo "-d is destination IP, which is where the packet is addressed to go; should be set to the address of the sniffer so that it is received and processed; default is 127.0.0.1"
  echo "-u is udp packets, which is the number of UDP packets that will be sent from that address; default is 5"
  echo "-t is tcp packets, which is the number of TCP packets that will be sent from that address; default is 0"
  echo "-p is tcp port, which is the port at which TCP packets will be sent from; default is 31"
  echo "-h is help, which prints this message."
}

sourceIP=10.27.151.5
destIP=127.0.0.1
udpPackets=5
tcpPackets=0
tcpPort=31
udpDestport=20
tcpDestport=30
#offset=0

# Read Parameters
while [ "$1" != "" ]; do
    case "$1" in
        -h ) usage
              exit ;;
        -s ) $sourceIP=$1 ;;
        -d ) $destIP=$1 ;;
        -u ) $udpPackets=$1 ;;
        -t ) $tcpPackets=$1 ;;
        -p ) $tcpPort=$1 ;;
    esac
    shift
done

# Check sourceIP validity; must not be empty
if [ $sourceIP = "" ]; then
    echo "Invalid sourceIP; exiting"
    exit
fi

# Check packet count validity; at least one must be greater than zero
if [ $udpPackets -lt 1 ] && [ $tcpPackets -lt 1 ]; then
    echo "Zero packets to be sent; exiting"
    exit
fi

# Check port validity; 22 is allowed for ssh traffic (though will not result in compromise), but must be 0-65535
if [ $tcpPort -lt 0 ] || [ $tcpPort -gt 65535 ]; then
    echo "TCP Port out of range; exiting"
    exit
fi

echo "Executing script with source IP $sourceIP, dest IP $destIP, UDP Packets $udpPackets, TCP Packets $tcpPackets, TCP Port $tcpPort"

# Check the UDP packet count
if [ $udpPackets -gt 0 ]; then
    # Perform UDP Packet sends for as many as configured
    for i in $(seq 1 $udpPackets);
    do
        # Vary destination port to ensure that it does not trigger the duplicate packet check
        #let offset=$i*5
        #$offset='expr $i * 5'
        #$udpDestport='expr $udpDestport + $offset'
        let udpDestport=$udpDestport+5
        sudo nping --udp --source-ip $sourceIP $destIP -p $udpDestport -c 1
        sleep 1
    done
fi

# Check the TCP packet count
if [ $tcpPackets -gt 0 ]; then
    # Perform TCP Packet sends for as many as configured
    for i in $(seq 1 $tcpPackets);
    do
        # Vary destination port to ensure that it does not trigger the duplicate packet check
        #$offset='expr $i * 5'
        #$tcpDestport='expr $tcpDestport + $offset'
        let tcpDestport=$tcpDestport+5
        sudo nping --tcp --source-ip $sourceIP $destIP -p $tcpDestport -g $tcpPort -c 1
        sleep 1
    done
fi
