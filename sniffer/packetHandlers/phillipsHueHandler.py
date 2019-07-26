import re
import time
import traceback

from networking.http import HTTP

# Global api uri pattern
api_uri_pattern = None

class PhillipsHueHandler:

    def __init__(self, config, logger):
        self.config = config["phillipsHue"]
        self.logger = logger
        self.api_requests = {}

        global api_uri_pattern
        api_uri_pattern = re.compile("/api/(.*)/")


    def handlePacket(self, tcp_packet, ip_packet):
        try:
            http = HTTP(tcp_packet.data)

            #strip out token
            match = api_uri_pattern.match(http.uri)
            if not match:
                print("http uri does not match api pattern")
                return
            else:
                token = match.group(1)
                self.trackAPIRequest(token, ip_packet.src)
    
        except Exception as ex:
            print("EXCEPTION: " +str(ex))
            traceback.print_exc()


    def trackAPIRequest(self, token, ip):
        #get all unique token requests for the IP address
        if ip not in self.api_requests.keys():
            requests = Requests()
            self.api_requests[ip] = requests
        else:
            requests = self.api_requests[ip]
        
        #determine if token has been used before    
        if token not in requests.token_set:
            print("new request from: " +str(ip)+ " with token: " +str(token))
            current_attempt_time = time.time()
            requests.addRequest(token, current_attempt_time)
            if len(requests.attempt_times) >= self.config["max_attempts"]:
                seconds_from_first_attempt = (current_attempt_time - requests.attempt_times[0]["time"])
                if seconds_from_first_attempt < self.config["max_attempts_interval_secs"]:
                    self.logBruteForce(ip)
                
                # If we've reached the max attempts, trim the first one and keep the other N-1 ones for future checks
                removed_request = requests.attempt_times.pop(0)
                requests.token_set.remove(removed_request["token"])


    def logBruteForce(self, ip):
        msg = ("BRUTE_FORCE: IP address " +str(ip)+ " has attempted device api calls with " +str(self.config["max_attempts"])+ 
                " different tokens within " +str(self.config["max_attempts_interval_secs"])+ " seconds")
        self.logger.warning(msg)


class Requests():

    def __init__(self):
        self.attempt_times = []
        self.token_set = set()

    def addRequest(self, token, current_attempt_time):
        self.attempt_times.append({"token": token, "time": current_attempt_time})
        self.token_set.add(token)
