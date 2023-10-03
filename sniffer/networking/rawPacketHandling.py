# 
#  Kalki - A Software-Defined IoT Security Platform
#  Copyright 2020 Carnegie Mellon University.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
#  [DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.
#  This Software includes and/or makes use of the following Third-Party Software subject to its own license:
#  1. Google Guava (https://github.com/google/guava) Copyright 2007 The Guava Authors.
#  2. JSON.simple (https://code.google.com/archive/p/json-simple/) Copyright 2006-2009 Yidong Fang, Chris Nokleberg.
#  3. JUnit (https://junit.org/junit5/docs/5.0.1/api/overview-summary.html) Copyright 2020 The JUnit Team.
#  4. Play Framework (https://www.playframework.com/) Copyright 2020 Lightbend Inc..
#  5. PostgreSQL (https://opensource.org/licenses/postgresql) Copyright 1996-2020 The PostgreSQL Global Development Group.
#  6. Jackson (https://github.com/FasterXML/jackson-core) Copyright 2013 FasterXML.
#  7. JSON (https://www.json.org/license.html) Copyright 2002 JSON.org.
#  8. Apache Commons (https://commons.apache.org/) Copyright 2004 The Apache Software Foundation.
#  9. RuleBook (https://github.com/deliveredtechnologies/rulebook/blob/develop/LICENSE.txt) Copyright 2020 Delivered Technologies.
#  10. SLF4J (http://www.slf4j.org/license.html) Copyright 2004-2017 QOS.ch.
#  11. Eclipse Jetty (https://www.eclipse.org/jetty/licenses.html) Copyright 1995-2020 Mort Bay Consulting Pty Ltd and others..
#  12. Mockito (https://github.com/mockito/mockito/wiki/License) Copyright 2007 Mockito contributors.
#  13. SubEtha SMTP (https://github.com/voodoodyne/subethasmtp) Copyright 2006-2007 SubEthaMail.org.
#  14. JSch - Java Secure Channel (http://www.jcraft.com/jsch/) Copyright 2002-2015 Atsuhiko Yamanaka, JCraft,Inc. .
#  15. ouimeaux (https://github.com/iancmcc/ouimeaux) Copyright 2014 Ian McCracken.
#  16. Flask (https://github.com/pallets/flask) Copyright 2010 Pallets.
#  17. Flask-RESTful (https://github.com/flask-restful/flask-restful) Copyright 2013 Twilio, Inc..
#  18. libvirt-python (https://github.com/libvirt/libvirt-python) Copyright 2016 RedHat, Fedora project.
#  19. Requests: HTTP for Humans (https://github.com/psf/requests) Copyright 2019 Kenneth Reitz.
#  20. netifaces (https://github.com/al45tair/netifaces) Copyright 2007-2018 Alastair Houghton.
#  21. ipaddress (https://github.com/phihag/ipaddress) Copyright 2001-2014 Python Software Foundation.
#  DM20-0543
#
#
import struct
import array
import socket
import random
import binascii


# Constructs a tcp response packet given a response string
def build_tcp_response(response, ip_packet, tcp_packet, set_fin, seq_offset):
    is_syn = False
    is_fin = set_fin

    # Get source/dest from sending packet
    src_ip = ip_packet.target
    dest_ip = ip_packet.src
    src_port = tcp_packet.dest_port
    dest_port = tcp_packet.src_port

    # Encode
    if isinstance(response, str):
        response = response.encode("utf-8")

    seq_num = tcp_packet.acknowledgment + seq_offset # in case several data messages are going out in sequence, add the seq offset from the previous message
    ack_num = tcp_packet.sequence + len(tcp_packet.data)
    tcp_header = createTCPHeader(response, is_syn, is_fin, seq_num, ack_num, src_port, dest_port, src_ip, dest_ip)

    # Create the Ethernet Frame header; swap dest & src macs to send back to sender
    eth_frame = createEthFrame(tcp_packet.src_mac, tcp_packet.dest_mac)

    # Create & populate the IP header; include length of tcp header and payload
    packet_length = len(tcp_header) + len(response)
    ip_header = createIPHeader(src_ip, dest_ip, packet_length)

    # Put the ack and response packets together
    responsePacket = eth_frame + ip_header + tcp_header + response

    # Return both the packet and the size of the tcp payload in case it is required for seq number offsets
    return responsePacket, len(response)


# Constructs a basic TCP SYN/ACK packet in order to ack an initial connection request
def build_tcp_syn_ack(ip_packet, tcp_packet):
    # Get source/dest from sending packet and swap to reply
    src_ip = ip_packet.target
    dest_ip = ip_packet.src
    src_port = tcp_packet.dest_port
    dest_port = tcp_packet.src_port

    seq_num = random.randrange(1000000000)  # Pick a random staring sequence number, per normal TCP rules
    ack_num = tcp_packet.sequence + 1 # We are acknowledging the initial sequence number, so use that + 1
    ack_tcp_header = createTCPHeader("".encode("utf-8"), True, False, seq_num, ack_num, src_port, dest_port, src_ip, dest_ip)

    # Create & populate the IP header
    ip_header = createIPHeader(src_ip, dest_ip, len(ack_tcp_header))

    # Create the Ethernet Frame header; swap dest & src macs to send back to sender
    eth_frame = createEthFrame(tcp_packet.src_mac, tcp_packet.dest_mac)

    # Put the ack and response packets together
    ackPacket = eth_frame + ip_header + ack_tcp_header
    return ackPacket

# Constructs a basic TCP ACK packet in order to acknowledge a data or fin message message
def build_tcp_ack(ip_packet, tcp_packet, is_fin):
    # Get source/dest from sending packet and swap to reply
    src_ip = ip_packet.target
    dest_ip = ip_packet.src
    src_port = tcp_packet.dest_port
    dest_port = tcp_packet.src_port

    seq_num = tcp_packet.acknowledgment  # Sequence # of a basic acknowledge message will always be the ack of the message that you are responding to

    # If we are ACKing a fin message from the remote host, set the ack # to the seq # + 1
    if is_fin:
        ack_num = tcp_packet.sequence + 1
    # For non-fin data messages, we are acknowledging the data, so add the size of the data to the given sequence #
    else:
        ack_num = tcp_packet.sequence + len(tcp_packet.data)

    ack_tcp_header = createTCPHeader("".encode("utf-8"), False, False, seq_num, ack_num, src_port, dest_port, src_ip, dest_ip)

    # Create & populate the IP header
    ip_header = createIPHeader(src_ip, dest_ip, len(ack_tcp_header))

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
def createIPHeader(source_ip, destination_ip, packet_len):
    # Constants
    version = 4
    ihl = 5
    tos = 0
    ident = 54321  # Arbitrary number; could be random (?)
    frag_offset = 0  # Should be zero for non-truncated packets
    ttl = 64
    prot = socket.IPPROTO_TCP

    # Length of the whole IP packet is the IP header plus the TCP header + data;
    # packet_len should give TCP header + data; IP packet header will always be 20 due to setting ihl to 5.
    total_length = 20 + packet_len

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