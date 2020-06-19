import socket
import binascii
import struct
import subprocess
import json
import os


tool_pipe = subprocess.PIPE

ETH_P_ALL = 3

def get_mac_addr(mac_raw):
    byte_str = map('{:02x}'.format, mac_raw)
    mac_addr = ':'.join(byte_str).upper()
    return mac_addr


class Ethernet:

    def __init__(self, raw_data):

        dest, src, prototype = struct.unpack('!6s6sH', raw_data[:14])

        self.dest_mac = get_mac_addr(dest)
        self.src_mac = get_mac_addr(src)
        self.proto = socket.htons(prototype)
        self.data = raw_data[14:]

out, err = subprocess.Popen("brctl show", shell=True, stdout=tool_pipe, stderr=tool_pipe).communicate()
outArr = out.decode().split("\n")[2].split("\t")[-1]
print(outArr)

eth2Socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))
eth2Socket.bind((outArr, 0))

while(True):
    raw_data, addr = eth2Socket.recvfrom(65535)
    eth = Ethernet(raw_data)
    print(raw_data)