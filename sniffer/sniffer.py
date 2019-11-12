#!/usr/bin/env python3
# NOTE: this needs to be run with sudo and python 3. This will only work on Linux due to the use of the AF_SOCKET type.

import socket
import logging
import sys
import json
import traceback

import netifaces

from networking.ethernet import Ethernet
from networking.ipv4 import IPv4
from networking.tcp import TCP

from packetHandlers.httpAuthHandler import HttpAuthHandler
from packetHandlers.phillipsHueHandler import PhillipsHueHandler
from packetHandlers.ipConnectionsHandler import IpConnectionsHandler

from utils import stats
from utils import email

# Internal parameters.
LOG_FILE_PATH = "sniffer.log"

# "Protocol" number used in Linux to indicate we want to listen to ALL packets.
ETH_P_ALL = 3

# Global logger.
logger = None


class HandlerResults:

    def __init__(self):
        self.echo_decision = True
        self.issues_found = []
        self.direct_messages_to_send = []


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


def bind_raw_socket(nic, action, nic_type):
    raw_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
    raw_socket.bind((nic, 0))
    print("{} on raw socket on interface {}...".format(action, nic), flush=True)
    nic_mac = netifaces.ifaddresses(nic)[netifaces.AF_LINK][0]['addr']
    print("Local MAC on {} NIC is {}\n".format(nic_type, nic_mac), flush=True)
    return raw_socket


def main():
    global logger
    logger = setup_custom_logger("main", LOG_FILE_PATH)

    config = load_config()

    handler_names = config["handlers"]
    echo_on = config["echo"] == "on"
    restricted_list = config["restrictedIPs"]

    # Set up stat logging if enabled in the configuration
    stat_logging_on = config["stat_logging"] == "on"
    if stat_logging_on:
        stat_logger = stats.StatLogger(logger, config["stat_interval"])

    # Set up email if enabled in the configuration
    email_on = config["email"] == "on"
    if email_on is True:
        email_server = email.EmailServer(config["emailConfig"])

    # Set up combined result object
    combined_results = HandlerResults()

    # Use the passed in command line arguments to create and set the correct handler
    handlers = []
    for handler_name in handler_names:
        if handler_name == "httpAuth":
            handlers.append(HttpAuthHandler(config, logger, combined_results))
        elif handler_name == "phillipsHue":
            handlers.append(PhillipsHueHandler(config, logger, combined_results))
        elif handler_name == "ipConnections":
            handlers.append(IpConnectionsHandler(config, logger, combined_results))
        else:
            print("Invalid handler name {} in config file".format(handler_name), flush=True)
    if len(handlers) == 0:
        print('No valid handler names found, proceeding with zero configured handlers.', flush=True)
    else:
        print("Initializing handlers {}".format(handlers), flush=True)

    incoming = bind_raw_socket(config["incomingNIC"], "Listening", "incoming")
    outgoing = bind_raw_socket(config["outgoingNIC"], "Echoing back", "outgoing")
    direct = bind_raw_socket(config["directNIC"], "Echoing back direct packets", "direct")

    last_data = None
    last_echo = None
    while True:
        # Received data from raw socket.
        raw_data, addr = incoming.recvfrom(65535)

        # Ignore duplicate packets
        if last_data == raw_data:
            continue

        last_data = raw_data
        ipv4 = None

        # Reset results for this iteration of results; assume no issues or messages to forward, and the packet should be echoed
        combined_results.echo_decision = True
        combined_results.issues_found = []
        combined_results.direct_messages_to_send = []

        # Ethernet
        eth = Ethernet(raw_data)
        #print("Ethernet packet with src {}, dest {}, proto {} received...".format(eth.src_mac, eth.dest_mac, eth.proto), flush=True)
        # Ignore non-IPv4 packets
        if eth.proto == 8:  # IPv4
            ipv4 = IPv4(eth.data)
            #print("IPv4 packet with src {}, target {}, proto {} received...".format(ipv4.src, ipv4.target, ipv4.proto))

            # Process TCP packets
            if ipv4.proto == 6:  # TCP
                tcp = TCP(ipv4.data, eth)

                # Filter SSH packets as necessary; primarily during test
                #if tcp.src_port == 22 or tcp.dest_port == 22:
                    #continue
                #print("INCOMING: TCP packet found with macs {}|{}, src {}:{}, dest {}:{}, syn {}, ack {}, seq # {}, ack # {} ... data: [{}]".format(eth.src_mac, eth.dest_mac, ipv4.src, tcp.src_port, ipv4.target, tcp.dest_port, tcp.flag_syn, tcp.flag_ack, tcp.sequence, tcp.acknowledgment, tcp.data), flush=True)

                for handler in handlers:
                    try:
                        handler.handleTCPPacket(tcp, ipv4)
                    except Exception as ex:
                        print("Handler exception: " + str(ex), flush=True)
                        traceback.print_exc()

            # Process UDP packets
            elif ipv4.proto == 17: # UDP
                for handler in handlers:
                    try:
                        handler.handleUDPPacket(ipv4)
                    except Exception as ex:
                        print("Handler exception: " + str(ex), flush=True)
                        traceback.print_exc()

            # Process the output of the handlers
            for result in combined_results.issues_found:
                for action in config["action_list"][result]:
                    if action == "ALERT":
                        print("ALERT: " + result + " detected!", flush=True)
                    elif action == "EMAIL" and email_on:
                        email_server.send_emails('Alert: ' + result, result + ' attempt detected from ' + ipv4.src)
                    elif action == "BLACKLIST":
                        print(result + " attempt detected from " + ipv4.src + "; adding to restricted list", flush=True)
                        restricted_list.append(ipv4.src)

            # Send any generated messages to their targets via the Direct NIC
            for message in combined_results.direct_messages_to_send:
                print("Sending response message!")
                direct.send(message)

            # Do stat logging if enabled
            if stat_logging_on:
                stat_logger.log_packet_statistics(ipv4)

        # Only echo packet if it is IPv4, echo is on, src IP is not restricted, no handler asked to drop, and we are not repeating data.
        if echo_on and (ipv4 is not None and ipv4.src not in restricted_list) and combined_results.echo_decision and last_echo != raw_data:
            try:
                outgoing.send(raw_data)
                last_echo = raw_data
            except Exception as e:
                print("Error echoing: " + str(e))


if __name__ == '__main__':
    main()
