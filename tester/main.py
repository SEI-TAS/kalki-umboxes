"""
A program that tests the functionalities of a umbox

To use, type:
sudo python3 main.py <TIMEOUT> <IP ADDRESS>  <PORT>
"""
import sys
from threading import Thread
from threadFunctions import *

ETH_P_ALL = 3
eth1_bridge_name = "br_eth1"

def main(timeout, ipAddr, port):

	eth1Socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
	eth1Socket.bind((eth1_bridge_name, 0))

	out, err = subprocess.Popen("brctl show", shell=True, stdout=tool_pipe, stderr=tool_pipe).communicate()
	outArr = out.decode().split("\n")[4].split("\t")[-1]

	eth2Socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
	eth2Socket.bind((outArr, 0))
	
	t1 = Thread(target=startSender, args=[eth1Socket, ipAddr, port])
	t2 = Thread(target=startReceiver, args=[eth2Socket])
	t3 = Thread(target=startQueueProcessor, args=[timeout])
	t4 = Thread(target=startAlertProcesser)

	t1.start()
	t2.start()
	t3.start()
	t4.start()


if(__name__=="__main__"):
	timeout = int(sys.argv[1])
	ip = sys.argv[2]
	port = int(sys.argv[3])
	main(timeout, ip, port)