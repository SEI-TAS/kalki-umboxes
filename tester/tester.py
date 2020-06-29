import socket
import binascii
import struct
import subprocess
import json
import time
from threading import Thread
import requests

def createEthFrameHeader(dest_mac, src_mac):
    ETH_P_IP = 0x0800
    rawFrame = struct.pack("!6s6sH", binascii.unhexlify(dest_mac.replace(":","")), binascii.unhexlify(src_mac.replace(":","")),ETH_P_IP)
    return rawFrame

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


tool_pipe = subprocess.PIPE

ETH_P_ALL = 3

sendQueue = []
recvQueue = []

out, err = subprocess.Popen("docker inspect eth1", shell=True, stdout=tool_pipe, stderr=tool_pipe).communicate()
data = json.loads(out)[0]
eth1MacDict = data["Containers"]
for key in eth1MacDict:
	eth1Mac = eth1MacDict[key]["MacAddress"]
out, err = subprocess.Popen("docker inspect umbox", shell=True, stdout=tool_pipe, stderr=tool_pipe).communicate()
data = json.loads(out)[0]
umboxMac = data["NetworkSettings"]["MacAddress"]
out, err = subprocess.Popen("docker inspect alert-server", shell=True, stdout=tool_pipe, stderr=tool_pipe).communicate()
data = json.loads(out)[0]
alertAddress = data["NetworkSettings"]["Networks"]["eth0"]["IPAddress"]

eth1Socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
eth1Socket.bind(("br_eth1", 0))

out, err = subprocess.Popen("brctl show", shell=True, stdout=tool_pipe, stderr=tool_pipe).communicate()
outArr = out.decode().split("\n")[4].split("\t")[-1]

eth2Socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
eth2Socket.bind((outArr, 0))

ip = 'netflix.com'
HOST = ip    # The remote host
PORT = 80              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
query = 'GET / HTTP/1.1\r\nHost: ' + ip + '\r\n\r\n'

def startSender():
	while True:
		s.send(query.encode())
		payload = s.recv(65535)
		raw_data = createEthFrameHeader(umboxMac, eth1Mac)+payload
		eth1Socket.send(raw_data)
		sendQueue.append(raw_data)
		time.sleep(1)

def startReceiver():
	while(True):
	    raw_data, addr = eth2Socket.recvfrom(65535)
	    if(addr[4] == binascii.unhexlify(eth1Mac.replace(":",""))):
	    	recvQueue.append(raw_data)
	    time.sleep(1)

def startQueueProcessor():
	lastTime = time.time()
	while(True):
		if(len(sendQueue) > 0 and len(recvQueue) > 0 and sendQueue[0] == recvQueue[0]):
			data = sendQueue.pop(0)
			recvQueue.pop(0)
			print("Sent and Received ", data)
			lastTime = time.time()
		elif(len(sendQueue) > 0 and time.time() - lastTime > 3):
			notFound = sendQueue.pop(0)
			print("Not Received: ", notFound)
			lastTime = time.time()
		time.sleep(1)

def startAlertProcesser():
	while(True):
		x = requests.get("http://"+alertAddress+":6060/")
		contents = x.content.decode()
		if(len(contents.split("\n")) > 1):
			print(contents)
		time.sleep(3)

t1 = Thread(target=startSender)
t2 = Thread(target=startReceiver)
t3 = Thread(target=startQueueProcessor)
t4 = Thread(target=startAlertProcesser)

t1.start()
t2.start()
t3.start()
t4.start()

#To send UDP instead of TCP change SOCK_STREAM to SOCK_DGRAM. 
