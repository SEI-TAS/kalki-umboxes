#!/usr/bin/env python3
# NOTE: this needs to be run with sudo and python 3. This will only work on Linux due to the use of the AF_SOCKET type.

import socket
import logging
import sys
import json

import netifaces

from networking.ethernet import Ethernet
from networking.ipv4 import IPv4
from networking.tcp import TCP

from packetHandlers.httpAuthHandler import HttpAuthHandler

# Internal parameters.
LOG_FILE_PATH = "sniffer.log"
ECHO_ON = False

# "Protocol" number used in Linux to indicate we want to listen to ALL packets.
ETH_P_ALL = 3

# Global logger.
logger = None

# Global handler.
handler = None


def setup_custom_logger(name, file_path):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler(file_path, mode='w')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger

def load_config():
    """Loads config from external file."""
    with open("config.json") as json_config:
        config = json.load(json_config)
    return config


def main():

    global logger
    logger = setup_custom_logger("main", LOG_FILE_PATH)

    config = load_config()

    #use the passed in command line arguments to create and set the correct handler
    global handler
    handler = HttpAuthHandler(config, logger);

    conn = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
    conn.bind((config["nic"], 0))
    print("Listening on raw socket on interface {}...".format(config["nic"]), flush=True)

    nic_mac = netifaces.ifaddresses(config["nic"])[netifaces.AF_LINK][0]['addr']
    print("Local MAC on NIC is {}\n".format(nic_mac), flush=True)

    last_tcp_sequence = 0
    while True:
        # Received data from raw socket.
        raw_data, addr = conn.recvfrom(65535)

        if ECHO_ON:
            # Echo it back before processing, to act transparently.
            print("Echoing data received back through raw socket.", flush=True)
            conn.send(raw_data)

        # Ethernet
        eth = Ethernet(raw_data)
        #print("Ethernet packet with src {}, dest {}, proto {} received...".format(eth.src_mac, eth.dest_mac, eth.proto), flush=True)
        if eth.proto != 8:  # IPv4
            # Ignore non-IPv4 packets
            continue

        # IPv4
        ipv4 = IPv4(eth.data)
        #print("IPv4 packet with src {}, target {}, proto {} received...".format(ipv4.src, ipv4.target, ipv4.proto))
        if ipv4.proto != 6:  # TCP
            # Ignore non-TCP IPv4 packets.
            continue

        # TCP
        tcp = TCP(ipv4.data)
        #print("TCP packet found with src port {}, dest port {} ... data: [{}]".format(tcp.src_port, tcp.dest_port, tcp.data), flush=True)
        if len(tcp.data) == 0 or tcp.dest_port != config["port"]:
            continue

        # Avoid duplicate packets.
        #print("\nTCP sequence: " + str(tcp.sequence), flush=True)
        if tcp.sequence == last_tcp_sequence:
            print("Ignoring duplicate TCP packet", flush=True)
            continue
        else:
            last_tcp_sequence = tcp.sequence

        handler.handlePacket(tcp);


if __name__ == '__main__':
    main()
