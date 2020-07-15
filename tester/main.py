"""
A program that tests the functionalities of a umbox

To use, type:
sudo python3 main.py <TIMEOUT> <IP ADDRESS>  <PORT>
"""
import sys
from threading import Thread
from helper import *
from threadFunctions import *
import argparse

ETH_P_ALL = 3
eth1_bridge_name = "br_eth1"
veths = getVeth()
eth2_veth = veths[0]
eth3_veth = veths[1]

def main(timeout, interface, udp, parser):

	eth1Socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
	eth1Socket.bind((eth1_bridge_name, 0))

	eth2Socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
	eth2Socket.bind((eth2_veth, 0))

	eth3Socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
	eth3Socket.bind((eth3_veth, 0))
	
	t1 = Thread(target=startSender, args=[eth1Socket, interface, udp])
	t2 = Thread(target=startReceiverETH2, args=[eth2Socket])
	t3 = Thread(target=startReceiverETH3, args=[eth3Socket])
	t4 = Thread(target=startQueueProcessor, args=[timeout, parser])
	t5 = Thread(target=startAlertProcesser)

	t1.start()
	t2.start()
	t3.start()
	t4.start()
	t5.start()


if(__name__=="__main__"):
	parser = argparse.ArgumentParser()
	parser.add_argument("--time", type=int, help="enter time to wait for checker",
                    nargs='?', default=3)
	parser.add_argument("--interface", type=str, help="enter interface",
                    nargs='?', default="wlp3s0")
	parser.add_argument("--parser", type=int, help="enter parsing function number",
                    nargs='?', default=0)
	parser.add_argument("--udp", action="store_true")
	
	args = vars(parser.parse_args())
	main(args["time"], args["interface"], args["udp"], args["parser"])