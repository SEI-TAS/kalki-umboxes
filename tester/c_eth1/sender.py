import socket
import subprocess
import json
import binascii

import struct

ETH_P_ALL = 3
network = "eth1"
src = "e1"
dest = "umbox"

def createEthFrameHeader(dest_mac, src_mac):
    ETH_P_IP = 0x0800
    rawFrame = struct.pack("!6s6sH", binascii.unhexlify(dest_mac.replace(":","")), binascii.unhexlify(src_mac.replace(":","")),ETH_P_IP)
    return rawFrame



raw_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
raw_socket.bind((network, 0))

src_Mac = "02:42:ac:1f:00:03"
dest_Mac = "02:42:ac:1f:00:02"

destSrcString = createEthFrameHeader(dest_Mac, src_Mac)

payload = ("["*30)+"PAYLOAD"+("]"*30)
ethertype = "\x08\x01"

data = destSrcString+ethertype+payload.encode()
print("success")
while(True):
	#print("D")
	raw_socket.send(data)