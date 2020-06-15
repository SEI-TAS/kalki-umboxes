import socket

ETH_P_ALL = 3

raw_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
raw_socket.bind(("eth2", 0))

while True:
	raw_data, addr = raw_socket.recvfrom(65535)
	print(raw_data)