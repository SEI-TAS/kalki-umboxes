import re
import time
import traceback

# Global Authorization pattern
basic_authorization_pattern = None

class HttpAuthHandler:

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.login_requests = {}

        global basic_authorization_pattern
        basic_authorization_pattern = re.compile('Authorization: Basic (.*)')


    def handlePacket(self, tcp_packet):
        try:
            http = HTTP(tcp_packet.data)
            http_info = str(http.data).split('\n')
            print("Received HTTP data: " + str(http.data), flush=True)
            for line in http_info:
                if 'Authorization' in line:
                    try:
                        match = basic_authorization_pattern.match(line)
                        if match:
                            print("Found line with authorization info: " + line, flush=True)
                            credentials = b64decode(match.group(1)).decode("ascii")
                            print("Credentials: " + credentials, flush=True)
                            username, password = credentials.split(":")
                            if username == self.config["default_username"] and password == self.config["default_password"]:
                                log_default_creds(tcp_packet.src_port)
                            track_login(tcp_packet.src_port, username)
                    except Exception as ex:
                        print("Exception processing credentials: " + str(ex), flush=True)
                        traceback.print_exc()
        except Exception as ex:
            print("HTTP exception: " + str(ex), flush=True)
            traceback.print_exc()


    def track_login(self, ip, user_name):
        # print("in tracking " + ip + " " + user_name)
        key = hash(ip + user_name)
        if key not in login_requests.keys():
            login_request = LoginRequest(ip, user_name, self.config["max_attempts"])
            self.login_requests[key] = login_request
        else:
            login_request = login_requests[key]
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
        msg = "DEFAULT_CRED: Login attempt with default credentials from " + ip
        self.logger.warning(msg)
        print(msg)
        return


class LoginRequest:
    def __init__(self, ip, user, max_attempts):
        self.ip = ip
        self.user = user
        self.count = 1
        self.delete = 0
        self.attempt_times = [0] * max_attempts
        self.attempt_times[0] = time.time()


