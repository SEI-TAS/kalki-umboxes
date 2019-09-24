import re
import time
import traceback

from urllib.parse import urlparse
from networking.http import HTTP

# Global api uri pattern
api_uri_pattern = None

class PhillipsHueHandler:

    def __init__(self, config, logger, result):
        self.config = config["phillipsHue"]
        self.logger = logger
        self.api_requests = {}
        self.token_requests = {}
        self.last_log_time = 0
        self.result = result

        global api_uri_pattern
        api_uri_pattern = re.compile("/api/(.*)/")


    def handlePacket(self, tcp_packet, ip_packet):
        try:
            http = HTTP(tcp_packet.data)
        except:
            # Disable the failure decision pending further review as this exception should not cause the packet to not be echoed
            #self.result.echo_decision = False
            return

        try:
            request_path = urlparse(http.uri).path

            #strip out token
            match = api_uri_pattern.match(http.uri)

            #check if the uri is just a request for username ("/api")
            if request_path == "/api":
                self.trackTokenRequest(ip_packet.src)
            elif match:
                token = match.group(1)
                self.trackAPIRequest(token, ip_packet.src)
            else:
                # Disable the failure decision pending further review as this exception should not cause the packet to not be echoed
                #self.result.echo_decision = False
                return

            if self.config["restrictAPI"] == "on" and http.method != "GET":
                print("restricted API request method: " +str(http.method))
                # This failure SHOULD result in not echoing the packet
                self.result.echo_decision = False
                return
            else:
                return

        except Exception as ex:
            print("EXCEPTION: " +str(ex))
            traceback.print_exc()
            # Disable the failure decision pending further review as this exception should not cause the packet to not be echoed
            #self.result.echo_decision = False
            return


    def trackAPIRequest(self, token, ip):
        #get all unique token requests for the IP address
        if ip not in self.api_requests.keys():
            requests = Requests()
            self.api_requests[ip] = requests
        else:
            requests = self.api_requests[ip]
        
        #determine if token has been used before    
        if token not in requests.token_set:
            current_attempt_time = time.time()
            requests.addRequest(token, current_attempt_time)
            if len(requests.attempt_times) >= self.config["max_attempts"]:
                seconds_from_first_attempt = (current_attempt_time - requests.attempt_times[0]["time"])

                # Only check for Brute Force if it is in the config file
                if "BRUTE_FORCE" in self.config["check_list"]:
                    if seconds_from_first_attempt < self.config["max_attempts_interval_secs"]:
                        self.logBruteForceAPI(ip)
                
                # If we've reached the max attempts, trim the first one and keep the other N-1 ones for future checks
                removed_request = requests.attempt_times.pop(0)
                requests.token_set.remove(removed_request["token"])

    def trackTokenRequest(self, ip):
        if ip not in self.token_requests.keys():
            attempt_times = []
            self.token_requests[ip] = attempt_times
        else:
            attempt_times = self.token_requests[ip]
        
        current_attempt_time = time.time()
        attempt_times.append(current_attempt_time)
        if len(attempt_times) >= self.config["max_attempts"]:
            seconds_from_first_attempt = (current_attempt_time - attempt_times[0])

            # Only check for Brute Force if it is in the config file
            if "BRUTE_FORCE" in self.config["check_list"]:
                if seconds_from_first_attempt < self.config["max_attempts_interval_secs"]:
                    self.logBruteForceToken(ip)
                
            # If we've reached the max attempts, trim the first one and keep the other N-1 ones for future checks
            attempt_times.pop(0)


    def logBruteForceAPI(self, ip):
        current_time = time.time()
        if(current_time - self.last_log_time > self.config["logging_timeout"]):
            msg = ("BRUTE_FORCE: IP address " +str(ip)+ " has attempted device api calls with " +str(self.config["max_attempts"])+ 
                " different tokens within " +str(self.config["max_attempts_interval_secs"])+ " seconds")
            self.logger.warning(msg)
            self.last_log_time = current_time
            self.result.issues_found.append("BRUTE_FORCE")


    def logBruteForceToken(self, ip):
        current_time = time.time()
        if(current_time - self.last_log_time > self.config["logging_timeout"]):
            msg = ("BRUTE_FORCE: IP address " +str(ip)+ " has attempted to get a token " +str(self.config["max_attempts"])+ 
                " times within " +str(self.config["max_attempts_interval_secs"])+ " seconds")
            self.logger.warning(msg)
            self.last_log_time = current_time
            self.result.issues_found.append("BRUTE_FORCE")


class Requests():

    def __init__(self):
        self.attempt_times = []
        self.token_set = set()

    def addRequest(self, token, current_attempt_time):
        self.attempt_times.append({"token": token, "time": current_attempt_time})
        self.token_set.add(token)
