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

import binascii
import struct
import subprocess
import json
import socket

tool_pipe = subprocess.PIPE
inspect_umbox = "docker inspect umbox"
inspect_alert_server = "docker inspect alert-server"
bridge_show = "brctl show"

class IPv4:

	def __init__(self, raw_data):
		version_header_length = raw_data[0]
		self.version = version_header_length >> 4
		self.header_length = (version_header_length & 15) * 4
		#self.total_packet_length = int.from_bytes(raw_data[2:4], "big", False)
		self.total_packet_length, self.ttl, self.proto, src, target = struct.unpack('! 2x H 4x B B 2x 4s 4s', raw_data[:20])
		self.src = self.ipv4(src)
		self.target = self.ipv4(target)
		self.data = raw_data[self.header_length:]

	# Returns properly formatted IPv4 address
	def ipv4(self, addr):
		return '.'.join(map(str, addr))



# Returns MAC as string from bytes (ie AA:BB:CC:DD:EE:FF)
def get_mac_addr(mac_raw):
	byte_str = map('{:02x}'.format, mac_raw)
	mac_addr = ':'.join(byte_str).upper()
	return mac_addr


class Ethernet:

	def __init__(self, raw_data):

		dest, src, prototype = struct.unpack('! 6s 6s H', raw_data[:14])

		self.dest_mac = get_mac_addr(dest)
		self.src_mac = get_mac_addr(src)
		self.proto = socket.htons(prototype)
		self.data = raw_data[14:]




"""
Creates Eth Frame Header. Original code at sniffer/networking/rawPacketHandling.py
"""
def createEthFrameHeader(dest_mac, src_mac):
	ETH_P_IP = 0x0800
	rawFrame = struct.pack("!6s6sH", binascii.unhexlify(dest_mac.replace(":","")), binascii.unhexlify(src_mac.replace(":","")),ETH_P_IP)
	return rawFrame

"""
Obtains the MAC address of the specified device
  - 0 for eth1_device
  - 1 for umbox
"""
def getMac(device):
	process = subprocess.Popen(inspect_umbox, shell=True, stdout=tool_pipe, stderr=tool_pipe)
	out,err = process.communicate()
	if(process.returncode != 0):
		raise Exception(err)

	data = json.loads(out)[0]
	if(device == 0):
		return data["NetworkSettings"]["Networks"]["eth1_device"]["MacAddress"]
	elif(device == 1):
		return data["NetworkSettings"]["MacAddress"]
	raise Exception("Invalid device number for getMac")

# Gets the alert-server IP address
def getAlertIP():
	process = subprocess.Popen(inspect_alert_server, shell=True, stdout=tool_pipe, stderr=tool_pipe)
	out,err = process.communicate()
	if(process.returncode != 0):
		raise Exception(err)

	data = json.loads(out)[0]
	return data["NetworkSettings"]["Networks"]["eth0_device"]["IPAddress"]

def getVeth():
	out, err = subprocess.Popen(bridge_show, shell=True, stdout=tool_pipe, stderr=tool_pipe).communicate()
	outList = out.decode().split("\n")
	br2I = -1
	br3I = -1
	for i in range(len(outList)):
		if("br_eth2" in outList[i]):
			br2I = i
		elif("br_eth3" in outList[i]):
			br3I = i
	eth2_veth = outList[br2I].split("\t")[-1]
	eth3_veth = outList[br3I].split("\t")[-1]
	return (eth2_veth, eth3_veth)