import re
import os
import time
import traceback
import hashlib

from networking.http import HTTP
from base64 import b64decode

# Global Authorization pattern
basic_authorization_pattern = None

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
        try:
            http = HTTP(tcp_packet.data)
        except:
            return False

        if http.authorization != None:
            try:
                auth_line = "Authorization: " + http.authorization
                match = basic_authorization_pattern.match(auth_line)
                if match:
                    credentials = b64decode(match.group(1)).decode("ascii")
                    username, password = credentials.split(":")
                    return self.authenticateUser(username, password)
                else:
                    #send a 407 authenticate response
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