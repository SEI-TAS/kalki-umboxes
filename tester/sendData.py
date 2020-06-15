import socket
import binascii
import struct
import subprocess
import json


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
umboxMac = data["NetworkSettings"]["MacAddress"]


raw_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
raw_socket.bind(("br_eth1", 0))

destSrcString = createEthFrameHeader(umboxMac, eth1Mac)

payload = ("TEST_PAYLOAD"*10)

data = destSrcString+payload.encode()
raw_socket.send(data)
print(eth1Mac, umboxMac) 
