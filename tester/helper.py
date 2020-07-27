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