import struct
import array
import socket
import random
import binascii

# Constructs an acknowledgement packet to a tcp packet and a response TCP message given a response string;
# Constructs the raw packets to send and adds them to a provided response list.
def build_response(response, ip_packet, tcp_packet, responseList):
    is_syn = False
    is_fin = False

    # Get source/dest from sending packet
    src_ip = ip_packet.target
    dest_ip = ip_packet.src
    src_port = tcp_packet.dest_port
    dest_port = tcp_packet.src_port

    # Encode
    if isinstance(response, str):
        response = response.encode("utf-8")

    # Create & populate the IP header
    ip_header = createIPHeader(src_ip, dest_ip)
    seq_num = tcp_packet.acknowledgment
    ack_num = tcp_packet.sequence + len(tcp_packet.data)
    ack_tcp_header = createTCPHeader("".encode("utf-8"), is_syn, is_fin, seq_num, ack_num, src_port, dest_port, src_ip, dest_ip)
    tcp_header = createTCPHeader(response, is_syn, is_fin, seq_num, ack_num, src_port, dest_port, src_ip, dest_ip)

    # Create the Ethernet Frame header; swap dest & src macs to send back to sender
    eth_frame = createEthFrame(tcp_packet.src_mac, tcp_packet.dest_mac)

    # Put the ack and response packets together
    ackPacket = eth_frame + ip_header + ack_tcp_header
    responsePacket = eth_frame + ip_header + tcp_header + response

    # Add the packets to the response list
    responseList.append(ackPacket)
    responseList.append(responsePacket)


# Constructs a basic TCP SYN/ACK packet in order to ack an initial connection request
def build_tcp_syn_ack(ip_packet, tcp_packet):
    # Get source/dest from sending packet and swap to reply
    src_ip = ip_packet.target
    dest_ip = ip_packet.src
    src_port = tcp_packet.dest_port
    dest_port = tcp_packet.src_port

    # Create & populate the IP header
    ip_header = createIPHeader(src_ip, dest_ip)
    seq_num = random.randrange(1000000000)  # Pick a random staring sequence number, per normal TCP rules
    ack_num = tcp_packet.sequence + 1 # We are acknowledging the initial sequence number, so use that + 1
    ack_tcp_header = createTCPHeader("".encode("utf-8"), True, False, seq_num, ack_num, src_port, dest_port, src_ip, dest_ip)

    # Create the Ethernet Frame header; swap dest & src macs to send back to sender
    eth_frame = createEthFrame(tcp_packet.src_mac, tcp_packet.dest_mac)

    # Put the ack and response packets together
    ackPacket = eth_frame + ip_header + ack_tcp_header
    return ackPacket

def createEthFrame(dest_mac, src_mac):
    ETH_P_IP = 0x0800
    rawFrame = struct.pack("!6s6sH", binascii.unhexlify(dest_mac.replace(":","")), binascii.unhexlify(src_mac.replace(":","")),ETH_P_IP)
    return rawFrame

# Creates the header of an IPv4 packet given source & destination addresses
def createIPHeader(source_ip, destination_ip):
    version = 4
    ihl = 5
    tos = 0
    total_length = 40 # Length is assumed; may have to calculate this at some point
    ident = 54321  # Arbitrary number; could be random (?)
    frag_offset = 0  # Should be zero for non-truncated packets
    ttl = 64
    prot = socket.IPPROTO_TCP
    src_ip = socket.inet_aton (source_ip)
    dest_ip = socket.inet_aton (destination_ip)

    ip_ihl_ver = (version << 4) + ihl

    # Generate the checksum with the actual checksum value set to zero, then copy it back in
    chksum = 0
    initial_ipheader = struct.pack("!BBHHHBBH4s4s", ip_ihl_ver, tos, total_length, ident, frag_offset, ttl, prot, chksum, src_ip, dest_ip)
    chksum = build_IP_header_checksum(initial_ipheader)

    # Now repack the header with the checksum added
    ipheader = struct.pack("!BBHHHBBH4s4s", ip_ihl_ver, tos, total_length, ident, frag_offset, ttl, prot, chksum, src_ip, dest_ip)

    return ipheader

# Creates the header of a TCP packet, given source/dest IPs for the checksum, ports, and flags/values for customization
def createTCPHeader(data, is_syn, is_fin, seq_num, ack_seq_num, src_port, dest_port, source_ip, destination_ip):
    doff = 5
    tcp_syn = 1 if is_syn else 0
    tcp_fin = 1 if is_fin else 0
    tcp_rst = 0
    tcp_psh = 0
    tcp_ack = 1
    tcp_urg = 0
    tcp_window = socket.htons (8) # Minimum 8, normally larger
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

    psh = struct.pack('!4s4sBBH' , source_address , dest_address , placeholder , protocol , tcp_length)
    psh = psh + tcp_header + data

    tcp_check = build_tcp_header_checksum(psh)

    # make the tcp header again and fill the correct checksum - remember checksum is NOT in network byte order
    tcp_header = (struct.pack('!HHLLBBH' , src_port, dest_port, seq_num, ack_seq_num, tcp_offset_res, tcp_flags, tcp_window) +
                  struct.pack('H' , tcp_check) +
                  struct.pack('!H' , tcp_urg_ptr))

    return tcp_header

# Copied from Scapy, per Stack Overflow
def build_IP_header_checksum (pkt):
    if struct.pack("H",1) == "\x00\x01": # big endian
        if len(pkt) % 2 == 1:
            pkt += "\0"
        s = sum(array.array("H", pkt))
        s = (s >> 16) + (s & 0xffff)
        s += s >> 16
        s = ~s
        return s & 0xffff
    else:
        if len(pkt) % 2 == 1:
            pkt += "\0"
        s = sum(array.array("H", pkt))
        s = (s >> 16) + (s & 0xffff)
        s += s >> 16
        s = ~s
        return (((s>>8)&0xff)|s<<8) & 0xffff

# Copied from various places on the internet
def build_tcp_header_checksum(msg):
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
            print("Error calculating checksum", flush=True)

    # One's Complement
    s = s + (s >> 16)
    s = ~s & 0xffff

    return s