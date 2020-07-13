import socket
import requests
import time
from helper import *
import binascii
import netifaces as ni
import struct
from scapy.all import *

sendQueue = []
recvQueue = []

ETH_P_ALL = 3
eth1Mac = getMac(0)
umboxMac = getMac(1) 
alertAddress = getAlertIP()

# A thread that will send packets to the umbox
def startSender(eth1Socket, interface, udp):
	sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
	sock.bind((interface, 0))

	inter = ni.ifaddresses(interface)[ni.AF_LINK][0]['addr']
	while(True):
		raw_data, addr = sock.recvfrom(65535)
		eth = Ethernet(raw_data)
		ipv4 = IPv4(eth.data)
		#print(addr[4] == binascii.unhexlify(inter.replace(":","")), eth.proto, ipv4.proto)
		if(addr[4] == binascii.unhexlify(inter.replace(":","")) and \
			eth.proto == 8 and ((ipv4.proto == 17 and udp) or (ipv4.proto == 6 and not udp))):
			payload = createEthFrameHeader(umboxMac, eth1Mac)+raw_data[14:]
			#print()
			try:
				print("send payloads")
				sendQueue.append(payload)
				eth1Socket.send(payload)
			except:
				print("ERROR SENDING")
			
			#time.sleep(1)

# A thread that will receive packets from the eth2 of the umbox
def startReceiverETH2(eth2Socket):
	while(True):
	    raw_data, addr = eth2Socket.recvfrom(65535)
	    if(addr[4] == binascii.unhexlify(eth1Mac.replace(":",""))):
	    	recvQueue.append(raw_data)

# A thread that will receive packets from the eth3 of the umbox
def startReceiverETH3(eth3Socket):
	while(True):
	    raw_data, addr = eth3Socket.recvfrom(65535)
	    if(addr[4] == binascii.unhexlify(eth1Mac.replace(":",""))):
	    	recvQueue.append(raw_data)

# A thread that checks if what was sent was sent back
def startQueueProcessor(timeout):
	lastTime = time.time()
	while(True):
		time.sleep(0.5)
		
		if(len(sendQueue) > 0 and len(recvQueue) > 0 and sendQueue[0] == recvQueue[0]):
			data = sendQueue.pop(0)
			recvQueue.pop(0)
			print("Found")
			#print("Sent and Received ", data)
			lastTime = time.time()
		elif(len(sendQueue) > 0 and (len(recvQueue) > 0) and (time.time() - lastTime > timeout)):#(len(recvQueue) > 0) or
			notFound = sendQueue.pop(0)
			if((len(recvQueue) > 0)):
				print("Nonempty Recv")
			else:
				print("Timeout")
			#print("Not Received: ", notFound)
			lastTime = time.time()

# A thread that will recieve 
def startAlertProcesser():
	while(True):
		x = requests.get("http://"+alertAddress+":6060/")
		contents = json.loads(x.content.decode())
		if(len(contents) > 1):
			print("\n".join(contents))