import re
import time
import traceback

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
        self.last_log_time = 0

        global basic_authorization_pattern
        basic_authorization_pattern = re.compile('Authorization: Basic (.*)')

    def handleTCPPacket(self, tcp_packet, ip_packet):

        # The first thing to do is confirm that we have something to check/proxy enabled, and return if not
        if not self.config["check_list"] and self.config["proxy_auth_enabled"] != "on":
            # Nothing to do; return
            return

        # Empty TCP packets are only relevant to establishing connections; ignore for processing
        packet_has_data = (len(tcp_packet.data) > 0)

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
                #print("HTTP exception: " + str(ex), flush=True)
                pass

        # If proxy auth is enabled and there is data, process active logins and determine echoing
        if self.config["proxy_auth_enabled"] == "on":
            # Ignore all traffic coming from the proxy authentication server
            if tcp_packet.src_port == self.config["proxy_auth_port"]:
                pass
            # See if there's an active proxy login for this IP
            elif ip_packet.src in self.proxy_logins:
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
            # No active proxy login; if this is a non-HTTP packet with data and the NON_HTTP check is enabled, flag it and disable echoing
            elif packet_has_data and http is None and "NON_HTTP" in self.config["check_list"]:
                msg = "NON_HTTP: Non HTTP TCP traffic received without proxy auth completed, from " + str(ip_packet.src)
                self.logger.warning(msg)
                print(msg)
                self.result.issues_found.append("NON_HTTP")
                self.result.echo_decision = False
                print("Non-HTTP traffic sent from " + str(ip_packet.src) + " without proxy login", flush=True)
            # All other cases where a non-confirmed IP address sends a TCP packet with data; disable echoing
            elif packet_has_data:
                self.result.echo_decision = False
                #print("Denying echo of TCP packet that has HTTP data without proxy login, may however be successful login request; processing", flush=True)
            # Now process tcp connection requests on the configured port; requires a TCP packet with SYN set and ACK cleared
            elif tcp_packet.flag_syn == True and tcp_packet.flag_ack == False and tcp_packet.dest_port == self.config["proxy_auth_port"]:
                # TCP connection request received on the configured port. This could be a login request, allow to pass through
                print("TCP connection SYN message received at configured port " + str(self.config["proxy_auth_port"]), flush=True)

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
                            # Process a new auth request from the current IP, as long as it isn't the proxy auth server, and at the configured port
                            if ip_packet.src not in self.proxy_logins and tcp_packet.dest_port == self.config["proxy_auth_port"]:
                                # Check against the proper credentials
                                if username == self.config["proxy_auth_username"] and password == self.config["proxy_auth_password"]:
                                    # Successful login; mark the time and IP
                                    print("Successful proxy login from " + str(ip_packet.src), flush=True)
                                    new_login = ProxyLogin()
                                    self.proxy_logins[ip_packet.src] = new_login
                                else:
                                    # Failed login; respond with HTTP error and log if enabled
                                    if "FAILED_AUTH" in self.config["check_list"]:
                                        msg = "FAILED_AUTH: HTTP request with incorrect authentication credentials, with proxy auth enabled; from " + str(ip_packet.src)
                                        self.logger.warning(msg)
                                        print(msg)
                                        self.result.issues_found.append("FAILED_AUTH")

                        # Only process multiple logins if it is in the config file
                        if "MULTIPLE_LOGIN" in self.config["check_list"]:
                            self.track_logins(ip_packet.src, username)

                except Exception as ex:
                    print("Exception processing credentials: " + str(ex), flush=True)
                    traceback.print_exc()

            # If no http basic credentials provided (or exception), proxy auth is enabled, and there is no successful login, log & respond
            if self.config["proxy_auth_enabled"] == "on" and not authorization_credentials and ip_packet.src not in self.proxy_logins:
                # Only log the error if in check list
                if "NO_AUTH" in self.config["check_list"]:
                    # Log/Report NO_AUTH error
                    msg = "NO_AUTH: HTTP request without authentication credentials with proxy auth enabled from " + str(ip_packet.src)
                    self.logger.warning(msg)
                    print(msg)
                    self.result.issues_found.append("NO_AUTH")

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


class LoginRequest:
    def __init__(self, ip, user, max_attempts):
        self.ip = ip
        self.user = user
        self.count = 1
        self.delete = 0
        self.attempt_times = [0] * max_attempts
        self.attempt_times[0] = time.time()
