import re
import time
import traceback

from networking.http import HTTP

# Global api uri pattern
api_uri_pattern = None

class PhillipsHueHandler:

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

        global api_uri_pattern
        api_uri_pattern = re.compile("/api/(.*)/")

    def handlePacket(self, tcp_packet, ip_packet):
        try:
            http = HTTP(tcp_packet.data)
            print("Received HTTP request: \n" +
                "Method: " +http.method+ "\n" +
                "URI: " +http.uri+ "\n" +
                "Version: " +http.version+ "\n" +
                "Host: " +str(http.host)+ "\n" +
                "Authorization: " +str(http.authorization)+ "\n")

            #strip out token
            match = api_uri_pattern.match(http.uri)
            if not match:
                print("http uri does not match api pattern")
                return
            else:
                token = match.group(1)
                print("token: " +str(token))
            
            #check if the src ip has used that token before 
            
            #add a new token entry with the time of request
            #if that ip has used the max number of tokens, check the time difference from the first
            #if the time difference is less than the threshold, append a brute force to the log
        except Exception as ex:
            print("EXCEPTION: " +str(ex))
            traceback.print_exc()

