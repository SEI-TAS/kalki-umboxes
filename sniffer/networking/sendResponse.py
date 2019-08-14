#!/

import socket
import struct

def sendResponse(response, ip_packet, tcp_packet):
    #flip src and dest to send back to origin of request
    srcIP = ip_packet.target
    destIP = ip_packet.src
    srcPort = tcp_packet.dest_port
    destPort = tcp_packet.src_port

    ipsock = socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_RAW)

    if isinstance(response, str):
        response = response.encode("utf-8")

    ip_header = createIPHeader(srcIP, destIP)

    seq_num = tcp_packet.acknowledgment
    ack_num = tcp_packet.sequence + len(tcp_packet.data)
    ack_tcp_header = createTCPHeader("".encode("utf-8"), seq_num, ack_num, srcPort, destPort, srcIP, destIP)
    tcp_header = createTCPHeader(response, seq_num, ack_num, srcPort, destPort, srcIP, destIP)

    ackPacket = ip_header + ack_tcp_header
    packet = ip_header + tcp_header + response

    #send an acknowledgement to the request
    ipsock.sendto(ackPacket, (destIP, destPort))

    #send the response to the request
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

# checksum function needed to calculate TCP checksums
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
