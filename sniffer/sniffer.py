#!/usr/bin/env python3
# NOTE: this needs to be run with sudo and python 3. This will only work on Linux due to the use of the AF_SOCKET type.

import socket
import logging
import sys
import json
import traceback

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import netifaces

from networking.ethernet import Ethernet
from networking.ipv4 import IPv4
from networking.tcp import TCP

from packetHandlers.httpAuthHandler import HttpAuthHandler
from packetHandlers.phillipsHueHandler import PhillipsHueHandler
from packetHandlers.udooNeoHandler import UdooNeoHandler

# Internal parameters.
LOG_FILE_PATH = "sniffer.log"

# "Protocol" number used in Linux to indicate we want to listen to ALL packets.
ETH_P_ALL = 3

# Global logger.
logger = None

# Global handler.
handler = None

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

def setup_email_login(host, port, username, password):
    # Try to connect 3 times
    retry_count = 3
    while retry_count > 0:
        try:
            # Establish Connection
            email_server = smtplib.SMTP(host=host, port=port, timeout=3)

            # Start TLS
            email_server.starttls()
            email_server.login(username, password)

            # Successful connection; return the server object
            print ("Email reporting set up successfully.", flush=True)
            return email_server
        except: #socket.timeout:
            print("Failed to connect to " + host + ":" + port + "; Exception: " + sys.exc_info()[0] + "; trying again", flush=True)
            retry_count = retry_count - 1

    print ("Failed to connect to " + host + ":" + port + ".  Email unavailable.", flush=True)
    return None

def setup_email_no_login(host, port):
    # Try to connect 3 times
    retry_count = 3
    while retry_count > 0:
        try:
            # Establish Connection
            email_server = smtplib.SMTP(host=host, port=port, timeout=3)

            # Successful connection; return the server object
            print ("Email reporting set up successfully.", flush=True)
            return email_server
        except socket.timeout:
            print("Failed to connect to " + host + ":" + port + ", trying again", flush=True)
            retry_count = retry_count - 1

    print ("Failed to connect to " + host + ":" + port + ".  Email unavailable.", flush=True)
    return None

def send_email(email_server, source_address, destination_address, email_subject, email_body):
    # Make sure the email server is connected
    if email_server == None:
        print ("No valid email server connection.  Email not sent.", flush=True)
        return

        # Email server connection confirmed; Create the message to send
    msg = MIMEMultipart()
    msg['From'] = source_address
    msg['To'] = destination_address
    msg['Subject'] = email_subject
    msg.attach(MIMEText(email_body, 'plain'))

    # Send the message via the provided server
    try:
        email_server.send_message(msg)
    except smtplib.SMTPException:
        print("Failed to send email to " + destination_address, flush=True)

    # Clean up the message
    del msg

def main():
    global logger
    logger = setup_custom_logger("main", LOG_FILE_PATH)

    config = load_config()

    handler_names = config["handlers"]
    echo_on = config["echo"] == "on"
    email_on = config["email"] == "on"
    restricted_list = config["restrictedIPs"]

    # Set up email if enabled in the configuration
    if email_on == True:
        # Get the basic email attributes
        email_server_address = config["emailConfig"]["email_server_address"]
        email_server_port = config["emailConfig"]["email_server_port"]
        email_source_address = config["emailConfig"]["email_source_address"]

        # Check to see if the server needs to be logged into
        if config["emailConfig"]["email_server_login"] == "on":
            # Get the username/password for logging in, and execute log in process
            email_username = config["emailConfig"]["email_account_username"]
            email_password = config["emailConfig"]["email_account_password"]
            email_server = setup_email_login(email_server_address, email_server_port, email_username, email_password)
        else:
            # Set up email server without logging in
            email_server = setup_email_no_login(email_server_address, email_server_port)

    # Set up combined result object
    combined_results = HandlerResults()

    #use the passed in command line arguments to create and set the correct handler
    #global handlers
    handlers = []
    for handler_name in handler_names:
        if handler_name ==  "httpAuth":
            handlers.append(HttpAuthHandler(config, logger, combined_results))
        elif handler_name == "phillipsHue":
            handlers.append(PhillipsHueHandler(config, logger, combined_results))
        elif handler_name == "udooNeo":
            handlers.append(UdooNeoHandler(config, logger, combined_results))
        else:
            print("Invalid handler name {} in config file".format(handler_name), flush=True)
    if len(handlers) == 0:
        print ('No valid handler names found, proceeding with zero configured handlers.', flush=True)
    else:
        print ("Initializing handlers {}".format(handlers), flush=True)

    incoming = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
    incoming.bind((config["incomingNIC"], 0))
    print("Listening on raw socket on interface {}...".format(config["incomingNIC"]), flush=True)

    incoming_nic_mac = netifaces.ifaddresses(config["incomingNIC"])[netifaces.AF_LINK][0]['addr']
    print("Local MAC on incoming NIC is {}\n".format(incoming_nic_mac), flush=True)

    outgoing = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
    outgoing.bind((config["outgoingNIC"], 0))
    print("Echoing back on raw socket on interface {}...".format(config["outgoingNIC"]), flush=True)

    outgoing_nic_mac = netifaces.ifaddresses(config["outgoingNIC"])[netifaces.AF_LINK][0]['addr']
    print("Local MAC on outgoing NIC is {}\n".format(outgoing_nic_mac), flush=True)

    direct = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
    direct.bind((config["directNIC"], 0))
    print("Echoing back on raw socket on interface {}...".format(config["directNIC"]), flush=True)

    direct_nic_mac = netifaces.ifaddresses(config["directNIC"])[netifaces.AF_LINK][0]['addr']
    print("Local MAC on direct NIC is {}\n".format(direct_nic_mac), flush=True)


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
                    elif action == "EMAIL" and email_on == True:
                        for destination_address in config["emailConfig"]["email_destination_address_list"]:
                            send_email(email_server, email_source_address, destination_address, 'Alert: ' + result, result + ' attempt detected from ' + ipv4.src)
                    elif action == "BLACKLIST":
                        print(result + " attempt detected from " + ipv4.src + "; adding to restricted list", flush=True)
                        restricted_list.append(ipv4.src)

            # Send any generated messages to their targets via the Direct NIC
            for message in combined_results.direct_messages_to_send:
                print("Sending response message!")
                direct.send(message)

            # Send any messages from the configured port (assumed to be responses from the proxy Python server) through the direct NIC
            if "httpAuth" in handler_names and config["httpAuth"]["proxy_auth_enabled"] == "on" and tcp.src_port == config["httpAuth"]["proxy_auth_port"]:
                direct.send(raw_data)

        # Only echo packet if echo is on and src IP is not restricted
        if echo_on and (ipv4 is not None and ipv4.src not in restricted_list) and combined_results.echo_decision and last_echo != raw_data:
            outgoing.send(raw_data)
            last_echo = raw_data


if __name__ == '__main__':
    main()