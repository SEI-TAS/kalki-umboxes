import socket
import binascii
import struct
import subprocess
import json


tool_pipe = subprocess.PIPE

ETH_P_ALL = 3

def get_mac_addr(mac_raw):
    byte_str = map('{:02x}'.format, mac_raw)
    mac_addr = ':'.join(byte_str).upper()
    return mac_addr


class Ethernet:

    def __init__(self, raw_data):

        dest, src, prototype = struct.unpack('!6s6sH', raw_data[:14])

        self.dest_mac = get_mac_addr(dest)
        self.src_mac = get_mac_addr(src)
        self.proto = socket.htons(prototype)
        self.data = raw_data[14:]


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


eth1Socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
eth1Socket.bind(("br_eth1", 0))

eth2Socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
eth2Socket.bind(("br_eth2", 0))

eth3Socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
eth3Socket.bind(("br_eth3", 0))

destSrcString = createEthFrameHeader(umboxMac, eth1Mac)

payload = ("TEST_PAYLOAD"*10)

data = destSrcString+payload.encode()

print("Data Sent: {} to {}".format(eth1Mac, umboxMac))
eth1Socket.send(data)
while(True):
	raw_data, addr = eth2Socket.recvfrom(65535)
	print(raw_data)
