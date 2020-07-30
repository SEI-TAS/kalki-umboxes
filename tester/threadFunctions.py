# 
#  Kalki - A Software-Defined IoT Security Platform
#  Copyright 2020 Carnegie Mellon University.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
#  [DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.
#  This Software includes and/or makes use of the following Third-Party Software subject to its own license:
#  1. Google Guava (https://github.com/google/guava) Copyright 2007 The Guava Authors.
#  2. JSON.simple (https://code.google.com/archive/p/json-simple/) Copyright 2006-2009 Yidong Fang, Chris Nokleberg.
#  3. JUnit (https://junit.org/junit5/docs/5.0.1/api/overview-summary.html) Copyright 2020 The JUnit Team.
#  4. Play Framework (https://www.playframework.com/) Copyright 2020 Lightbend Inc..
#  5. PostgreSQL (https://opensource.org/licenses/postgresql) Copyright 1996-2020 The PostgreSQL Global Development Group.
#  6. Jackson (https://github.com/FasterXML/jackson-core) Copyright 2013 FasterXML.
#  7. JSON (https://www.json.org/license.html) Copyright 2002 JSON.org.
#  8. Apache Commons (https://commons.apache.org/) Copyright 2004 The Apache Software Foundation.
#  9. RuleBook (https://github.com/deliveredtechnologies/rulebook/blob/develop/LICENSE.txt) Copyright 2020 Delivered Technologies.
#  10. SLF4J (http://www.slf4j.org/license.html) Copyright 2004-2017 QOS.ch.
#  11. Eclipse Jetty (https://www.eclipse.org/jetty/licenses.html) Copyright 1995-2020 Mort Bay Consulting Pty Ltd and others..
#  12. Mockito (https://github.com/mockito/mockito/wiki/License) Copyright 2007 Mockito contributors.
#  13. SubEtha SMTP (https://github.com/voodoodyne/subethasmtp) Copyright 2006-2007 SubEthaMail.org.
#  14. JSch - Java Secure Channel (http://www.jcraft.com/jsch/) Copyright 2002-2015 Atsuhiko Yamanaka, JCraft,Inc. .
#  15. ouimeaux (https://github.com/iancmcc/ouimeaux) Copyright 2014 Ian McCracken.
#  16. Flask (https://github.com/pallets/flask) Copyright 2010 Pallets.
#  17. Flask-RESTful (https://github.com/flask-restful/flask-restful) Copyright 2013 Twilio, Inc..
#  18. libvirt-python (https://github.com/libvirt/libvirt-python) Copyright 2016 RedHat, Fedora project.
#  19. Requests: HTTP for Humans (https://github.com/psf/requests) Copyright 2019 Kenneth Reitz.
#  20. netifaces (https://github.com/al45tair/netifaces) Copyright 2007-2018 Alastair Houghton.
#  21. ipaddress (https://github.com/phihag/ipaddress) Copyright 2001-2014 Python Software Foundation.
#  DM20-0543
#
#

import socket
import requests
import time
from helper import *
import binascii
import netifaces as ni
import struct
from scapy.all import *
from networkParser import *

sendQueue = []
recvQueue = []

ETH_P_ALL = 3
eth1Mac = getMac(0)
umboxMac = getMac(1) 
alertAddress = getAlertIP()

outgoing = open("outgoing.log", "w")

# A thread that will send packets to the umbox
def startSender(eth1Socket, interface, udp):
	sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
	sock.bind((interface, 0))

	inter = ni.ifaddresses(interface)[ni.AF_LINK][0]['addr']
	while(True):
		raw_data, addr = sock.recvfrom(65535)
		eth = Ethernet(raw_data)
		ipv4 = IPv4(eth.data)
		if(addr[4] == binascii.unhexlify(inter.replace(":","")) and \
			eth.proto == 8 and ((ipv4.proto == 17 and udp) or (ipv4.proto == 6 and not udp))):
			payload = createEthFrameHeader(umboxMac, eth1Mac)+raw_data[14:]
			try:
				outgoing.write(str((payload)))
				outgoing.write("\n")
				outgoing.flush()
				sendQueue.append(payload)
				eth1Socket.send(payload)
				print("SENT!")
			except Exception as e:
				print(e)

# A thread that will receive packets from the eth2 of the umbox
def startReceiverETH2(eth2Socket):
	while(True):
	    raw_data, addr = eth2Socket.recvfrom(65535)
	    if(addr[4] == binascii.unhexlify(eth1Mac.replace(":",""))):
	    	recvQueue.append((raw_data, "ETH2"))

# A thread that will receive packets from the eth3 of the umbox
def startReceiverETH3(eth3Socket):
	while(True):
	    raw_data, addr = eth3Socket.recvfrom(65535)
	    recvQueue.append((raw_data, "ETH3"))

# A thread that checks if what was sent was sent back
def startQueueProcessor(timeout, n):
	lastTime = time.time()
	while(True):
		time.sleep(0.5)
		if(len(recvQueue)  > 0):
			dataRecv = recvQueue.pop(0)
			print(dataRecv[1], dataRecv[0])
		"""
		if(len(sendQueue) > 0 and len(recvQueue) > 0 and parser(n, (sendQueue[0]))== recvQueue[0][0]):
			data = sendQueue.pop(0)
			dataRecv = recvQueue.pop(0)
			print(dataRecv[1], dataRecv[0])
			#print("Found")
			lastTime = time.time()
		elif(len(sendQueue) > 0 and (len(recvQueue) > 0) and (time.time() - lastTime > timeout)):#(len(recvQueue) > 0) or
			notFound = sendQueue.pop(0)
			if((len(recvQueue) > 0)):
				print("Nonempty Recv")
			else:
				print("Timeout")
			lastTime = time.time()
		"""

# A thread that will recieve 
def startAlertProcesser():
	while(True):
		x = requests.get("http://"+alertAddress+":6060/")
		contents = json.loads(x.content.decode())
		if(len(contents) > 1):
			print("\n".join(contents))
