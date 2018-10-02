import socket
import time
import re
import logging
import traceback
from base64 import b64decode

from networking.ethernet import Ethernet
from networking.ipv4 import IPv4
from networking.tcp import TCP
from networking.http import HTTP

login_requests = {}

# Default credentials for the device
DEFAULT_USERNAME = "Username"
DEFAULT_PASSWORD = "Password"

LOG_FILE_PATH = "snort.log"
REPEATED_ATTEMPTS_INTERVAL_MINS = 30
MAX_ATTEMPTS = 4
IOT_SERVER_PORT = 9010


class LoginRequest:
    def __init__(self, ip, user):
        self.ip = ip
        self.user = user
        self.count = 1
        self.delete = 0
        self.attempt_times = [0] * MAX_ATTEMPTS
        self.attempt_times[0] = time.time()


def log_default_creds(ip):
    logging.warning("DEFAULT_CRED: Login attempt with default credentials from " + ip)
    return


def track_login(ip, user_name):
    # print("in tracking " + ip + " " + user_name)
    key = hash(ip + user_name)
    if key not in login_requests.keys():
        login_request = LoginRequest(ip, user_name)
        login_requests[key] = login_request
        print("Login attempt " + str(login_request.count))
    else:
        login_request = login_requests[key]
        login_request.count += 1
        print("Login attempt " + str(login_request.count))

        current_attempt_time = time.time()
        if login_request.count > MAX_ATTEMPTS: # There is duplication of packets
            time_from_last_attempt_in_minutes = (current_attempt_time - login_request.attempt_times[0]) / 60
            if time_from_last_attempt_in_minutes < REPEATED_ATTEMPTS_INTERVAL_MINS:
                logging.error("MULTIPLE_LOGIN : More than" + str(MAX_ATTEMPTS) + " attempts in " + str(time_from_last_attempt_in_minutes) + " minutes")

            # If we've reached the max attempts, trim the first one and keep the other N-1 ones for future checks.
            login_request.attempt_times = login_requests[1:]
            login_request.attempt_times.append(0)
            login_request.count -= 1

        # Store this last attempt.
        login_request.attempt_times[login_request.count - 1] = current_attempt_time


def main():
    basic_authorization_pattern = re.compile('Authorization: Basic (.*)')
    logging.basicConfig(filename=LOG_FILE_PATH, level=logging.DEBUG)
    conn = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))

    last_tcp_sequence = 0
    while True:
        raw_data, addr = conn.recvfrom(65535)
        eth = Ethernet(raw_data)
        # IPv4
        if eth.proto == 8:
            ipv4 = IPv4(eth.data)

            # TCP
            if ipv4.proto == 6:
                tcp = TCP(ipv4.data)

                if len(tcp.data) > 0:
                    # HTTP
                    if tcp.dest_port == IOT_SERVER_PORT:
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
