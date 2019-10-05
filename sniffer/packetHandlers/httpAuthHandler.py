import re
import time
import traceback
import socket
import struct

from networking.http import HTTP
from base64 import b64decode


class ProxyLogin:

    def __init__(self):
        self.confirmed_login = False
        self.auth_time = time.time()

# Global Authorization pattern
basic_authorization_pattern = None

class HttpAuthHandler:

    def __init__(self, config, logger, result):
        self.config = config["httpAuth"]
        self.logger = logger
        self.login_requests = {}
        self.result = result
        self.proxy_logins = {}

        global basic_authorization_pattern
        basic_authorization_pattern = re.compile('Authorization: Basic (.*)')

    def handleTCPPacket(self, tcp_packet, ip_packet):

        # The first thing to do is confirm that we have something to check/proxy enabled, and return if not
        if not self.config["check_list"] and self.config["proxy_auth_enabled"] != "on":
            # Nothing to do; return
            return

        # Empty TCP packets are only relevant to establishing connections; ignore for processing
        packet_has_data = (len(tcp_packet.data) == 0)

        # For non-empty packets, check to see if they are valid HTTP requests
        http = None
        if packet_has_data:
            try:
                http = HTTP(tcp_packet.data)
                print("Received HTTP request: \n" +
                      "Method: " + http.method + "\n" +
                      "URI: " + http.uri + "\n" +
                      "Version: " + http.version + "\n" +
                      "Host: " + str(http.host) + "\n" +
                      "Authorization: " + str(http.authorization) + "\n")
            except Exception as ex:
                print("HTTP exception: " + str(ex), flush=True)

        # If proxy auth is enabled, process active logins and determine echoing
        if self.config["proxy_auth_enabled"] == "on":
            # See if there's an active proxy login for this IP
            if ip_packet.src in self.proxy_logins:
                # If the current IP is not yet confirmed, check timer window
                if self.proxy_logins[ip_packet.src].confirmed_login == False:
                    # If the timer window has not elapsed, confirm
                    if time.time() - self.proxy_logins[ip_packet.src].auth_time <= self.config["proxy_auth_login_timer"]:
                        # TCP packet sent within timer window; confirm this connection
                        self.proxy_logins[ip_packet.src].confirmed_login = True
                        print("Successful proxy login confirmation from " + str(ip_packet.src), flush=True)
                    else:
                        # TCP packet NOT sent within timer window; therefore cancel this authorization/disable echoing;
                        # TBD: log the packet that missed the timer(?)
                        del self.proxy_logins[ip_packet.src]
                        self.result.echo_decision = False
                        print("Proxy login timed out; no TCP packet received within " + str(self.config["proxy_auth_login_timer"]) + " sec from " + str(ip_packet.src), flush=True)
                # Proxy login is confirmed; see if configured timeout window has elapsed
                elif time.time() - self.proxy_logins[ip_packet.src].auth_time > self.config["proxy_auth_timeout"]:
                    # Proxy Auth timeout has been exceeded; kill the active login/disable echoing;
                    # TBD: log the packet that timed out the connection(?)
                    del self.proxy_logins[ip_packet.src]
                    self.result.echo_decision = False
                    print("Confirmed proxy login timed out after " + str(self.config["proxy_auth_timeout"]) + " sec for " + str(ip_packet.src), flush=True)
                # Confirmed proxy login that hasn't timed out; traffic is authorized and can be passed on
                else:
                    # TBD: Add logs/printouts as necessary
                    pass
            # No active proxy login; if this is a non-HTTP packet and the NON_HTTP check is enabled, flag it and disable echoing
            elif http is None and "NON_HTTP" in self.config["check_list"]:
                msg = "NON_HTTP: Non HTTP TCP traffic received without proxy auth completed, from " + str(ip_packet.src)
                self.logger.warning(msg)
                print(msg)
                self.result.issues_found.append("NON_HTTP")
                self.result.echo_decision = False
                print("Non-HTTP traffic sent from " + str(ip_packet.src) + " without proxy login", flush=True)
            # All other cases where a non-confirmed IP address sends a TCP packet; disable echoing
            else:
                self.result.echo_decision = False

        # Now process HTTP traffic
        if http is not None:
            authorization_credentials = False

            # Check to see if there are authorization credentials using Basic authorization
            if http.authorization is not None:
                try:
                    # Make sure basic authorization is matched
                    auth_line = "Authorization: " + http.authorization
                    match = basic_authorization_pattern.match(auth_line)
                    if match:
                        authorization_credentials = True
                        print("Found authorization info in http request: ", flush=True)
                        credentials = b64decode(match.group(1)).decode("ascii")
                        print("Credentials: " + credentials, flush=True)
                        username, password = credentials.split(":")

                        # Only check for Default Credentials if it is in the config file
                        if "DEFAULT_CRED" in self.config["check_list"]:
                            if username == self.config["default_username"] and password == self.config["default_password"]:
                                self.log_default_creds(ip_packet.src)

                        # Only process proxy auth if it is in the config file
                        if self.config["proxy_auth_enabled"] == "on":
                            # Process a new auth request from the current IP
                            if ip_packet.src not in self.proxy_logins:
                                # Check against the proper credentials
                                if username == self.config["proxy_auth_username"] and password == self.config["proxy_auth_password"]:
                                    # Successful login; mark the time and IP
                                    print("Successful proxy login from " + str(ip_packet.src), flush=True)
                                    new_login = ProxyLogin()
                                    self.proxy_logins[ip_packet.src] = new_login

                                    # Respond with a HTTP 200 OK message
                                    response = ("HTTP/1.1 200 OK \r\n" +
                                                "WWW-Authenticate: Basic \r\n" +
                                                "Connection: close \r\n\r\n")

                                    self.build_response(self, response, ip_packet, tcp_packet, self.result.direct_messages_to_send)

                                else:
                                    # Failed login; respond with HTTP error and log if enabled
                                    if "FAILED_AUTH" in self.config["check_list"]:
                                        msg = "FAILED_AUTH: HTTP request with incorrect authentication credentials, with proxy auth enabled; from " + str(ip_packet.src)
                                        self.logger.warning(msg)
                                        print(msg)
                                        self.result.issues_found.append("FAILED_AUTH")

                                    # Respond to sender with a HTTP 403 Forbidden error
                                    response = ("HTTP/1.1 403 Forbidden \r\n" +
                                                "WWW-Authenticate: Basic \r\n" +
                                                "Connection: close \r\n\r\n")

                                    self.build_response(self, response, ip_packet, tcp_packet, self.result.direct_messages_to_send)

                        # Only process multiple logins if it is in the config file
                        if "MULTIPLE_LOGIN" in self.config["check_list"]:
                            self.track_logins(ip_packet.src, username, password)

                except Exception as ex:
                    print("Exception processing credentials: " + str(ex), flush=True)
                    traceback.print_exc()

            # If no http basic credentials provided (or exception), proxy auth is enabled, and there is no successful login, log & respond
            if authorization_credentials == False and self.config["proxy_auth_enabled"] == "on" and ip_packet.src not in self.proxy_logins:
                # Only log the error if in check list
                if "NO_AUTH" in self.config["check_list"]:
                    # Log/Report NO_AUTH error
                    msg = "NO_AUTH: HTTP request without authentication credentials with proxy auth enabled from " + str(ip_packet.src)
                    self.logger.warning(msg)
                    print(msg)
                    self.result.issues_found.append("NO_AUTH")

                # Respond to sender with 401 error
                response = ("HTTP/1.1 401 Unauthorized \r\n" +
                            "WWW-Authenticate: Basic \r\n" +
                            "Connection: close \r\n\r\n")

                self.build_response(self, response, ip_packet, tcp_packet, self.result.direct_messages_to_send)

        return

    def handleUDPPacket(self, ip_packet):
        # This handler does not process UDP packets; simply return
        return

    def track_logins(self, ip, user_name):

        key = hash(str(ip) + user_name)
        if key not in self.login_requests.keys():
            login_request = LoginRequest(ip, user_name, self.config["max_attempts"])
            self.login_requests[key] = login_request
        else:
            login_request = self.login_requests[key]
            login_request.count += 1

            current_attempt_time = time.time()
            if login_request.count > self.config["max_attempts"]: # There is duplication of packets
                minutes_from_first_attempt = (current_attempt_time - login_request.attempt_times[0]) / 60.0
                print("Time from first attempt in mins: " + str(minutes_from_first_attempt))

                if minutes_from_first_attempt < self.config["max_attempts_interval_mins"]:
                    msg = "MULTIPLE_LOGIN : More than " + str(self.config["max_attempts"]) + " attempts in " + str(minutes_from_first_attempt) + " minutes from same IP address"
                    self.logger.error(msg)
                    print(msg)

                # If we've reached the max attempts, trim the first one and keep the other N-1 ones for future checks.
                login_request.attempt_times.pop(0)
                login_request.attempt_times.append(0)
                login_request.count -= 1

            # Store this last attempt.
            login_request.attempt_times[login_request.count - 1] = current_attempt_time

    def log_default_creds(self, ip):
        msg = "DEFAULT_CRED: Login attempt with default credentials from " + str(ip)
        self.logger.warning(msg)
        print(msg)
        self.result.issues_found.append("DEFAULT_CRED")
        return

    def build_response(self, response, ip_packet, tcp_packet, responseList):
        is_fin = False

        # Get source/dest from sending packet
        srcIP = ip_packet.target
        destIP = ip_packet.src
        srcPort = tcp_packet.dest_port
        destPort = tcp_packet.src_port

        # Encode
        if isinstance(response, str):
            response = response.encode("utf-8")

        # Create & populate the IP header
        ip_header = self.createIPHeader(srcIP, destIP)
        seq_num = tcp_packet.acknowledgment
        ack_num = tcp_packet.sequence + len(tcp_packet.data)
        ack_tcp_header = self.createTCPHeader(self, "".encode("utf-8"), is_fin, seq_num, ack_num, srcPort, destPort, srcIP, destIP)
        tcp_header = self.createTCPHeader(self, response, is_fin, seq_num, ack_num, srcPort, destPort, srcIP, destIP)

        # Put the ack and response packets together
        ackPacket = ip_header + ack_tcp_header
        responsePacket = ip_header + tcp_header + response

        # Add the packets to the response list
        responseList.append(ackPacket)
        responseList.append(responsePacket)

    def createIPHeader(source_ip, destination_ip):
        version = 4
        ihl = 5
        tos = 0
        total_length = 0
        ident = 54321
        frag_offset = 0
        ttl = 255
        prot = socket.IPPROTO_TCP
        chksum = 0
        src_ip = socket.inet_aton (source_ip)
        dest_ip = socket.inet_aton (destination_ip)

        ip_ihl_ver = (version << 4) + ihl

        ipheader = struct.pack("!BBHHHBBH4s4s", ip_ihl_ver, tos, total_length, ident, frag_offset, ttl, prot, chksum, src_ip, dest_ip)
        return ipheader

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
                print("Error calculating checksum", flush=True)

        # One's Complement

        s = s + (s >> 16)
        s = ~s & 0xffff

        return s

    def createTCPHeader(self, data, is_fin, seq_num, ack_seq_num, src_port, dest_port, source_ip, destination_ip):
        doff = 5
        tcp_fin = 1 if is_fin else 0
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

        tcp_check = self.checksum(psh)

        # make the tcp header again and fill the correct checksum - remember checksum is NOT in network byte order
        tcp_header = (struct.pack('!HHLLBBH' , src_port, dest_port, seq_num, ack_seq_num, tcp_offset_res, tcp_flags, tcp_window) +
                      struct.pack('H' , tcp_check) +
                      struct.pack('!H' , tcp_urg_ptr))

        return tcp_header


class LoginRequest:
    def __init__(self, ip, user, max_attempts):
        self.ip = ip
        self.user = user
        self.count = 1
        self.delete = 0
        self.attempt_times = [0] * max_attempts
        self.attempt_times[0] = time.time()


