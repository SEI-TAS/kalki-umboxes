import re
import os
import time
import traceback
import hashlib

from networking.http import HTTP
from networking.hijackTCP import sendResponse
from networking.hijackTCP import sendDeviceTeardown
from networking.hijackTCP import respondDeviceTeardown
from networking.hijackTCP import respondClientTeardown

from base64 import b64decode

# Global Authorization pattern
basic_authorization_pattern = None
check_for_device_fin = False
check_for_client_fin = False
client_ip = None
device_ip = None

class HttpAuthHandler:

    def __init__(self, config, logger):
        self.config = config["httpAuth"]
        self.logger = logger

        global basic_authorization_pattern
        basic_authorization_pattern = re.compile('Authorization: Basic (.*)')

        script_dir = os.path.dirname(__file__)
        rel_path = "../" +self.config["password_file"]
        self.password_file_path = os.path.join(script_dir, rel_path)


    def handlePacket(self, tcp_packet, ip_packet):
        global check_for_client_fin, check_for_device_fin
        global client_ip, device_ip

        try:
            http = HTTP(tcp_packet.data)
        except:

            if check_for_client_fin and self.isClientFin(ip_packet, tcp_packet):
                respondClientTeardown(ip_packet, tcp_packet)
                check_for_client_fin = False
            elif check_for_device_fin and self.isDeviceFin(ip_packet, tcp_packet):
                respondDeviceTeardown(ip_packet, tcp_packet)
                check_for_device_fin = False
            return False

        if http.authorization != None:
            try:
                auth_line = "Authorization: " + http.authorization
                match = basic_authorization_pattern.match(auth_line)
                if match:
                    credentials = b64decode(match.group(1)).decode("ascii")
                    username, password = credentials.split(":")
                    if self.authenticateUser(username, password):
                        return True
                    
                #send a 401 unauthorized response
                print("sending 401 response")
                response = ("HTTP/1.1 401 Unauthorized \r\n" +
                            "WWW-Authenticate: Basic \r\n" +
                            "Connection: close \r\n\r\n")
                sendResponse(response, ip_packet, tcp_packet)
                sendDeviceTeardown(ip_packet, tcp_packet)

                #set flag to search for fin from client
                check_for_client_fin = True
                client_ip = ip_packet.src

                #set flag to search for fin from device
                check_for_device_fin = True
                device_ip = ip_packet.target
                return False

            except Exception as ex:
                print("Exception processing credentials: " + str(ex), flush=True)
                traceback.print_exc()


    def authenticateUser(self, username, password):
        try:
            for line in open(self.password_file_path, "r").readlines():
                credentials = line.split(":")
                stored_user = credentials[0]
                stored_hash = credentials[1].rstrip()
                if username == stored_user:
                    return self.verifyPassword(stored_hash, password)
        except:
            print("error opening password file")

        return False


    def verifyPassword(self, stored_hash, to_verify):
        hash_method = self.config["hash_method"]
        if hash_method == "md5":
            m = hashlib.md5()
        else: 
            return False

        m.update(to_verify.encode('utf-8'))
        to_verify_hash = m.hexdigest()
        
        return stored_hash == to_verify_hash


    #check if the incoming packet has a matching IP for the client and has a fin flag set
    def isClientFin(self, ip_packet, tcp_packet):
        global client_ip
        return ip_packet.src == client_ip and tcp_packet.flag_fin

    #check if the incoming packet has a matching IP for the device and has a fin flag set
    def isDeviceFin(self, ip_packet, tcp_packet):
        global device_ip
        return ip_packet.src == device_ip and tcp_packet.flag_fin

