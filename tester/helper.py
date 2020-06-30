import binascii
import struct
import subprocess
import json

tool_pipe = subprocess.PIPE
inspect_umbox = "docker inspect umbox"
inspect_alert_server = "docker inspect alert-server"
bridge_show = "brctl show"

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
	eth2_veth = out.decode().split("\n")[4].split("\t")[-1]
	eth3_veth = out.decode().split("\n")[5].split("\t")[-1]
	return (eth2_veth, eth3_veth)