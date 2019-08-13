import re
import os
import socket
import struct
import time
import traceback
import hashlib

from networking.http import HTTP
from base64 import b64decode

# Global Authorization pattern
basic_authorization_pattern = None

class HttpAuthHandler:

    def __init__(self, config, logger):
        self.config = config["httpAuth"]
        self.logger = logger

        global basic_authorization_pattern
        basic_authorization_pattern = re.compile('Authorization: Basic (.*)')

        script_dir = os.path.dirname(__file__)
        rel_path = "../" +self.config["password_file"]
        self.password_file_path = os.path.join(script_dir, rel_path)


    def handlePacket(self, tcp_packet, ip_packet):
        try:
            http = HTTP(tcp_packet.data)
        except:
            return False

        if http.authorization != None:
            try:
                auth_line = "Authorization: " + http.authorization
                match = basic_authorization_pattern.match(auth_line)
                if match:
                    credentials = b64decode(match.group(1)).decode("ascii")
                    username, password = credentials.split(":")
                    if self.authenticateUser(username, password):
                        return True
                    
                #send a 401 unauthorized response
                print("sending 401 response")
                send401(ip_packet, tcp_packet)
                return False

            except Exception as ex:
                print("Exception processing credentials: " + str(ex), flush=True)
                traceback.print_exc()


    def authenticateUser(self, username, password):
        try:
            for line in open(self.password_file_path, "r").readlines():
                credentials = line.split(":")
                stored_user = credentials[0]
                stored_hash = credentials[1].rstrip()
                if username == stored_user:
                    return self.verifyPassword(stored_hash, password)
        except:
            print("error opening password file")

        return False


    def verifyPassword(self, stored_hash, to_verify):
        hash_method = self.config["hash_method"]
        if hash_method == "md5":
            m = hashlib.md5()
        else: 
            return False

        m.update(to_verify.encode('utf-8'))
        to_verify_hash = m.hexdigest()
        
        return stored_hash == to_verify_hash


def send401(ip_packet, tcp_packet):
    #flip src and dest to send back to origin of request
    srcIP = ip_packet.target
    destIP = ip_packet.src
    srcPort = tcp_packet.dest_port
    destPort = tcp_packet.src_port

    ipsock = socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_RAW)

    response = ("HTTP/1.1 401 Unauthorized \r\n" +
                "WWW-Authenticate: Basic \r\n" +
                "Connection: close \r\n\r\n").encode("utf-8")

    ip_header = createIPHeader(srcIP, destIP)

    seq_num = tcp_packet.acknowledgment
    ack_num = tcp_packet.sequence + len(tcp_packet.data)
    tcp_header = createTCPHeader(response, seq_num, ack_num, srcPort, destPort, srcIP, destIP)

    packet = ip_header + tcp_header + response

    ipsock.sendto(packet, (destIP, destPort))


#creates an IP header as a string of packed information
def createIPHeader(source_ip, destination_ip) :    
    version = 4
    ihl = 5
    tos = 0
    total_length = 0  #kernel computes this
    ident = 54321
    frag_offset = 0
    ttl = 255
    prot = socket.IPPROTO_TCP
    chksum = 0        #kernel computes this
    src_ip = socket.inet_aton (source_ip)
    dest_ip = socket.inet_aton (destination_ip)

    ip_ihl_ver = (version << 4) + ihl

    ipheader = struct.pack("!BBHHHBBH4s4s", ip_ihl_ver, tos, total_length, 
                           ident, frag_offset, ttl, prot, 
                           chksum, src_ip, dest_ip)
    return ipheader

#creates a packed TCP header given the data, flags, sequence and ack numbers
def createTCPHeader(data, seq_num, ack_seq_num, src_port, dest_port, source_ip, destination_ip) :
    doff = 5
    tcp_fin = 0
    tcp_syn = 0
    tcp_rst = 0
    tcp_psh = 0
    tcp_ack = 1
    tcp_urg = 0
    tcp_window = socket.htons (8)
    tcp_check = 0
    tcp_urg_ptr = 0

    tcp_offset_res = (doff << 4) + 0
    tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh << 3) + (tcp_ack << 4) + (tcp_urg << 5)

    tcp_header = struct.pack("!HHLLBBHHH" , src_port, dest_port, seq_num, 
                             ack_seq_num, tcp_offset_res, tcp_flags, 
                             tcp_window, tcp_check, tcp_urg_ptr)

    # pseudo header fields
    source_address = socket.inet_aton( source_ip )
    dest_address = socket.inet_aton(destination_ip)
    placeholder = 0
    protocol = socket.IPPROTO_TCP
    tcp_length = len(tcp_header) + len(data)

    psh = struct.pack('!4s4sBBH' , source_address , dest_address , placeholder , protocol , tcp_length);
    psh = psh + tcp_header + data;

    tcp_check = checksum(psh)

    # make the tcp header again and fill the correct checksum - remember checksum is NOT in network byte order
    tcp_header = (struct.pack('!HHLLBBH' , src_port, dest_port, seq_num, ack_seq_num, tcp_offset_res, tcp_flags, tcp_window) + 
            struct.pack('H' , tcp_check) + 
            struct.pack('!H' , tcp_urg_ptr))

    return tcp_header

# checksum function needed to calculate checksums
def checksum(msg):
    s = 0       # Binary Sum

    # loop taking 2 characters at a time
    for i in range(0, len(msg), 2):
        if (i+1) < len(msg):
            a = msg[i] 
            b = msg[i+1]
            s = s + (a+(b << 8))
        elif (i+1)==len(msg):
            s += msg[i]
        else:
            raise "Error calculating checksum"

    # One's Complement
    
    s = s + (s >> 16)
    s = ~s & 0xffff

    return s


