import socket
import requests
import time
from helper import *
import binascii

sendQueue = []
recvQueue = []

eth1Mac = getMac(0)
umboxMac = getMac(1) 
alertAddress = getAlertIP()

# A thread that will send packets to the umbox
def startSender(eth1Socket, ipAddr="google.com", port = 80):
	ip = ipAddr
	HOST = ip
	PORT = port
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	
	s.connect((HOST, PORT))
	query = 'GET / HTTP/1.1\r\nHost: ' + ip + '\r\n\r\n'
	while(True):
		s.send(query.encode())
		payload = s.recv(65535)
		raw_data = createEthFrameHeader(umboxMac, eth1Mac)+payload
		eth1Socket.send(raw_data)
		sendQueue.append(raw_data)
		time.sleep(1)

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
def startQueueProcessor(timeout=3):
	lastTime = time.time()
	while(True):
		if(len(sendQueue) > 0 and len(recvQueue) > 0 and sendQueue[0] == recvQueue[0]):
			data = sendQueue.pop(0)
			recvQueue.pop(0)
			print("Sent and Received ", data)
			lastTime = time.time()
		elif(len(sendQueue) > 0 and time.time() - lastTime > timeout):
			notFound = sendQueue.pop(0)
			print("Not Received: ", notFound)
			lastTime = time.time()

# A thread that will recieve 
def startAlertProcesser():
	while(True):
		x = requests.get("http://"+alertAddress+":6060/")
		contents = json.loads(x.content.decode())
		if(len(contents) > 1):
			print("\n".join(contents))