import socket

ETH_P_ALL = 3

raw_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
raw_socket.bind(("eth1", 0))

src_addr = "\x01\x02\x03\x04\x05\x06"
dst_addr = "\x01\x02\x03\x04\x05\x06"
payload = ("["*30)+"PAYLOAD"+("]"*30)
checksum = "\x1a\x2b\x3c\x4d"
ethertype = "\x08\x01"

data = dst_addr+src_addr+ethertype+payload+checksum
raw_socket.send(data.encode())

print("success")