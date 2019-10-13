import socket
import time

IP = "10.27.152.5"
PORT = 6000
MESSAGE = "test"
PACKETS = 10

print("Opening UDP socket")
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for i in range(PACKETS):
    curr_port = PORT+i
    print("Sending UDP packet to port " + curr_port)
    udp_socket.sendto(MESSAGE, (IP, curr_port))
    time.sleep(1)

print("Finished sending UDP packets")
