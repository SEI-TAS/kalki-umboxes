import socket
import binascii
import struct
import subprocess
import json
import os
import time

tool_pipe = subprocess.PIPE

ETH_P_ALL = 3

def createEthFrameHeader(dest_mac, src_mac):
    ETH_P_IP = 0x0800
    rawFrame = struct.pack("!6s6sH", binascii.unhexlify(dest_mac.replace(":","")), binascii.unhexlify(src_mac.replace(":","")),ETH_P_IP)
    return rawFrame


out, err = subprocess.Popen("docker inspect eth1", shell=True, stdout=tool_pipe, stderr=tool_pipe).communicate()
data = json.loads(out)[0]
eth1MacDict = data["Containers"]
for key in eth1MacDict:
	eth1Mac = eth1MacDict[key]["MacAddress"]

out, err = subprocess.Popen("docker inspect umbox", shell=True, stdout=tool_pipe, stderr=tool_pipe).communicate()
data = json.loads(out)[0]
#umboxMac = data["NetworkSettings"]["Networks"]["eth0"]["MacAddress"]
umboxMac = data["NetworkSettings"]["MacAddress"]

eth1Socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
eth1Socket.bind(("br_eth1", 0))

counter = 0
while True:
	#print("Data Sent: {} to {}".format(eth1Mac, umboxMac))
	payload = "TESTING Data for Connection: {}".format(counter)
	data = createEthFrameHeader(umboxMac, eth1Mac)+payload.encode()
	eth1Socket.send(data)
	print(data)
	time.sleep(1)
	counter += 1

#sysctl net.ipv4.conf.all.forwarding=1
#sudo iptables -P FORWARD ACCEPT
