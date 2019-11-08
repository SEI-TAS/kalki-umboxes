import re
import time
import traceback

from networking.http import HTTP
from networking.rawPacketHandling import build_tcp_syn_ack
from networking.rawPacketHandling import build_response
from base64 import b64decode


class LoginRequest:
    def __init__(self, ip, user, max_attempts):
        self.ip = ip
        self.user = user
        self.count = 1
        self.delete = 0
        self.attempt_times = [0] * max_attempts
        self.attempt_times[0] = time.time()


class ProxyLogin:
    def __init__(self):
        self.confirmed_login = False
        self.auth_time = time.time()


class HttpAuthHandler:
    def __init__(self, config, logger, result):
        self.config = config["httpAuth"]
        self.logger = logger
        self.login_requests = {}
        self.result = result
        self.last_log_time = 0

        self.proxy_logins = {}

        self.basic_authorization_pattern = re.compile('Authorization: Basic (.*)')
        self.digest_authorization_pattern = re.compile('Authorization: Digest username="([^"]*)"(.*)')

    def handleUDPPacket(self, ip_packet):
        # This handler does not process UDP packets; simply return
        return

    def handleTCPPacket(self, tcp_packet, ip_packet):
        # The first thing to do is confirm that we have something to check/proxy enabled, and return if not
        if not self.config["check_list"] and self.config["proxy_auth_enabled"] != "on":
            # Nothing to do; return
            return

        # For non-empty packets, check to see if they are valid HTTP requests
        http = None
        packet_has_data = (len(tcp_packet.data) > 0)
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
                # Non-HTTP packet with data was received.
                #print("HTTP exception: " + str(ex), flush=True)
                pass

        # Evaluate HTTP authentication requests.
        if http and http.authorization:
            try:
                username, password = self.parse_credentials(http.authorization)
                credentials_parsed = username is not None
                if credentials_parsed:
                    # Only check for Default Credentials if it is in the config file
                    if "DEFAULT_CRED" in self.config["check_list"]:
                        if username == self.config["default_username"] and (password == self.config["default_password"] or password is None):
                            self.log_default_creds(ip_packet.src)

                    # Only process multiple logins if it is in the config file
                    if "MULTIPLE_LOGIN" in self.config["check_list"]:
                        self.track_logins(ip_packet.src, username)

                    # Only process proxy auth if it is in the config file
                    if self.config["proxy_auth_enabled"] == "on":
                        self.proxy_process_auth_request(tcp_packet, ip_packet, username, password)
                else:
                    print("Authorization header received, but credentials could not be parsed.")

            except Exception as ex:
                print("Exception processing credentials: " + str(ex), flush=True)
                traceback.print_exc()

        if self.config["proxy_auth_enabled"] == "on":
            # If proxy is enabled, process which packets to pass through, and which replies to send back directly.
            self.proxy_process_packet(http, tcp_packet, ip_packet)

    def parse_credentials(self, authorization_info):
        """Obtain credential information from the authorization field value."""
        username = None
        password = None
        try:
            # Make sure basic or digest authorization is matched
            auth_line = "Authorization: " + authorization_info
            basic_match = self.basic_authorization_pattern.match(auth_line)
            digest_match = self.digest_authorization_pattern.match(auth_line)
            if basic_match or digest_match:
                print("Found authorization info in http request: ", flush=True)

                if basic_match:
                    credentials = b64decode(basic_match.group(1)).decode("ascii")
                    print("Credentials: " + credentials, flush=True)
                    username, password = credentials.split(":")
                else:
                    username = digest_match.group(1)
                    password = None
                    print("Username: " + username, flush=True)
        except Exception as ex:
            print("Exception processing credentials: " + str(ex), flush=True)
            traceback.print_exc()

        return username, password

    def proxy_process_auth_request(self, tcp_packet, ip_packet, username, password):
        """Process a new auth request from the current IP"""
        if ip_packet.src not in self.proxy_logins and tcp_packet.dest_port == self.config["proxy_auth_port"]:
            # Check against the proper credentials
            if username == self.config["proxy_auth_username"] and password == self.config["proxy_auth_password"]:
                # Successful login; mark the time and IP
                print("Successful proxy login from " + str(ip_packet.src), flush=True)
                new_login = ProxyLogin()
                self.proxy_logins[ip_packet.src] = new_login

                # Build a custom HTTP response to the successful login
                response = ("HTTP/1.1 200 OK \r\n" +
                            "WWW-Authenticate: Basic \r\n" +
                            "Connection: close \r\n\r\n")
                build_response(response, ip_packet, tcp_packet, self.result.direct_messages_to_send)

    def proxy_queue_unauthorized_reply(self, tcp_packet, ip_packet):
        """Builds and queues an Unauthorized HTTP reply, logging this too if needed."""
        # Only log the error if in check list
        if "FAILED_AUTH" in self.config["check_list"]:
            # Log/Report NO_AUTH error
            msg = "FAILED_AUTH: HTTP request without authentication or with invalid credentials with proxy auth enabled from " + str(ip_packet.src)
            self.logger.warning(msg)
            print(msg)
            self.result.issues_found.append("FAILED_AUTH")

        # Build a custom HTTP response to the lack of or invalidity of login credentials
        response = ("HTTP/1.1 401 Unauthorized \r\n" +
                    "WWW-Authenticate: Basic \r\n" +
                    "Connection: close \r\n\r\n")
        build_response(response, ip_packet, tcp_packet, self.result.direct_messages_to_send)

    def proxy_process_packet(self, http, tcp_packet, ip_packet):
        # See if there's an active proxy login for this IP.
        if ip_packet.src in self.proxy_logins:
            # Check and apply timeouts if needed, drop packet if timed out.
            self.result.echo_decision = self.proxy_check_auth_timeouts(ip_packet)

        # Handle IP that is not currently logged in successfully.
        if ip_packet.src not in self.proxy_logins:
            # A non-confirmed IP address sent a TCP packet; they won't be passed through.
            self.result.echo_decision = False

            if http:
                # HTTP messages while not logged in will get an unauthorized reply.
                self.proxy_queue_unauthorized_reply(tcp_packet, ip_packet)
            else:
                # TCP connection requests can be HTTP login connection attempts if sent to proxy port; reply to the directly.
                if tcp_packet.flag_syn and not tcp_packet.flag_ack and tcp_packet.dest_port == self.config["proxy_auth_port"]:
                    # TCP connection request received on the configured port. This could be a login request.
                    print("TCP connection SYN message received at configured port " + str(self.config["proxy_auth_port"]), flush=True)

                    # Build the SYN/ACK response to simulate a TCP connection, and put it in the queue for responding
                    self.result.direct_messages_to_send.append(build_tcp_syn_ack(ip_packet, tcp_packet))

    def proxy_check_auth_timeouts(self, ip_packet):
        """Check if initial timeout to wait for first packet after auth has elapsed, or if timeout for auth has elapsed as well."""
        # If the current IP is not yet confirmed, check timer window
        time_since_auth = time.time() - self.proxy_logins[ip_packet.src].auth_time
        if self.proxy_logins[ip_packet.src].confirmed_login is False:
            # If the timer window has not elapsed, confirm
            if time_since_auth <= self.config["proxy_auth_login_timer"]:
                # TCP packet sent within timer window; confirm this connection
                self.proxy_logins[ip_packet.src].confirmed_login = True
                print("Successful proxy login confirmation from " + str(ip_packet.src), flush=True)
                return True
            else:
                # TCP packet NOT sent within timer window; therefore cancel this authorization/disable echoing;
                # TBD: log the packet that missed the timer(?)
                del self.proxy_logins[ip_packet.src]
                print("Proxy login timed out; no TCP packet received within " + str(self.config["proxy_auth_login_timer"]) + " sec from " + str(ip_packet.src), flush=True)
                return False
        # Proxy login is confirmed; see if configured timeout window has elapsed
        else:
            if time_since_auth <= self.config["proxy_auth_timeout"]:
                # Auth has not timed out yet; nothing to do.
                return True
            else:
                # Proxy Auth timeout has been exceeded; kill the active login/disable echoing;
                # TBD: log the packet that timed out the connection(?)
                del self.proxy_logins[ip_packet.src]
                print("Confirmed proxy login timed out after " + str(self.config["proxy_auth_timeout"]) + " sec for " + str(ip_packet.src), flush=True)
                return False

    def track_logins(self, ip, user_name):
        """Track loging attempts, and log that if needed."""
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
                    self.log_multiple_attempts(minutes_from_first_attempt)

                # If we've reached the max attempts, trim the first one and keep the other N-1 ones for future checks.
                login_request.attempt_times.pop(0)
                login_request.attempt_times.append(0)
                login_request.count -= 1

            # Store this last attempt.
            login_request.attempt_times[login_request.count - 1] = current_attempt_time

    def log_multiple_attempts(self, minutes_from_first_attempt):
        current_time = time.time()
        if current_time - self.last_log_time > self.config["logging_timeout"]:
            msg = "MULTIPLE_LOGIN : More than " + str(self.config["max_attempts"]) + " attempts in " + str(minutes_from_first_attempt) + " minutes from same IP address"
            self.logger.warning(msg)
            self.last_log_time = current_time
            print(msg)
            self.result.issues_found.append("MULTIPLE_LOGIN")

    def log_default_creds(self, ip):
        msg = "DEFAULT_CRED: Login attempt with default credentials from " + str(ip)
        self.logger.warning(msg)
        print(msg)
        self.result.issues_found.append("DEFAULT_CRED")
