#!/usr/bin/env python3
# NOTE: this needs to be run with sudo and python 3. This will only work on Linux due to the use of the AF_SOCKET type.

import socket
import time
import re
import logging
import sys
import traceback
from base64 import b64decode

import netifaces

from networking.ethernet import Ethernet
from networking.ipv4 import IPv4
from networking.tcp import TCP
from networking.http import HTTP

login_requests = {}

# Default credentials for the device
DEFAULT_USERNAME = "Username"
DEFAULT_PASSWORD = "Password"

# Port to sniff on.
IOT_SERVER_PORT = 9010

# NIC to bind to.
NIC_NAME = "ens9"

# Internal parameters.
LOG_FILE_PATH = "sniffer.log"
REPEATED_ATTEMPTS_INTERVAL_MINS = 30
MAX_ATTEMPTS = 4
ECHO_ON = True

# "Protocol" number used in Linux to indicate we want to listen to ALL packets.
ETH_P_ALL = 3

# Global logger.
logger = None


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


class LoginRequest:
    def __init__(self, ip, user):
        self.ip = ip
        self.user = user
        self.count = 1
        self.delete = 0
        self.attempt_times = [0] * MAX_ATTEMPTS
        self.attempt_times[0] = time.time()


def log_default_creds(ip):
    msg = "DEFAULT_CRED: Login attempt with default credentials from " + ip
    logger.warning(msg)
    print(msg)
    return


def track_login(ip, user_name):
    # print("in tracking " + ip + " " + user_name)
    key = hash(ip + user_name)
    if key not in login_requests.keys():
        login_request = LoginRequest(ip, user_name)
        login_requests[key] = login_request
    else:
        login_request = login_requests[key]
        login_request.count += 1

        current_attempt_time = time.time()
        if login_request.count > MAX_ATTEMPTS: # There is duplication of packets
            minutes_from_first_attempt = (current_attempt_time - login_request.attempt_times[0]) / 60.0
            print("Time from first attempt in mins: " + str(minutes_from_first_attempt))
            if minutes_from_first_attempt < REPEATED_ATTEMPTS_INTERVAL_MINS:
                msg = "MULTIPLE_LOGIN : More than " + str(MAX_ATTEMPTS) + " attempts in " + str(minutes_from_first_attempt) + " minutes from same IP address"
                logger.error(msg)
                print(msg)

            # If we've reached the max attempts, trim the first one and keep the other N-1 ones for future checks.
            login_request.attempt_times.pop(0)
            login_request.attempt_times.append(0)
            login_request.count -= 1

        # Store this last attempt.
        login_request.attempt_times[login_request.count - 1] = current_attempt_time


def main():
    basic_authorization_pattern = re.compile('Authorization: Basic (.*)')

    global logger
    logger = setup_custom_logger("main", LOG_FILE_PATH)

    conn = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
    conn.bind((NIC_NAME, 0))
    print("Listening on raw socket on interface {}...\n".format(NIC_NAME))

    nic_mac = netifaces.ifaddresses('eth0')[netifaces.AF_LINK][0]['addr']
    print("Local MAC on NIC is {}".format(nic_mac))

    last_tcp_sequence = 0
    while True:
        # Received data from raw socket.
        raw_data, addr = conn.recvfrom(65535)

        if ECHO_ON:
            # Echo it back before processing, to act transparently.
            conn.send(raw_data)

        # Ethernet
        eth = Ethernet(raw_data)
        print("Ethernet packet with src {}, dest {}, proto {} received...".format(eth.src_mac, eth.dest_mac, eth.proto))
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
        print("TCP packet found with src port {}, dest port {} ... data: [{}]".format(tcp.src_port, tcp.dest_port, tcp.data))
        if len(tcp.data) == 0 or tcp.dest_port != IOT_SERVER_PORT:
            continue

        # Avoid duplicate packets.
        print("\nTCP sequence: " + str(tcp.sequence))
        if tcp.sequence == last_tcp_sequence:
            print("Ignoring duplicate TCP packet")
            continue
        else:
            last_tcp_sequence = tcp.sequence

        try:
            http = HTTP(tcp.data)
            http_info = str(http.data).split('\n')
            print("Received HTTP data: " + str(http.data))
            for line in http_info:
                if 'Authorization' in line:
                    try:
                        match = basic_authorization_pattern.match(line)
                        if match:
                            print("Found line with authorization info: " + line)
                            credentials = b64decode(match.group(1)).decode("ascii")
                            print("Credentials: " + credentials)
                            username, password = credentials.split(":")
                            if username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD:
                                log_default_creds(ipv4.src)
                            track_login(ipv4.src, username)
                    except Exception as ex:
                        print("Exception processing credentials: " + str(ex))
                        traceback.print_exc()
        except Exception as ex:
            print("HTTP exception: " + str(ex))
            traceback.print_exc()


if __name__ == '__main__':
    main()
