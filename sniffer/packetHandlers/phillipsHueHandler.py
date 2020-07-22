# 
#  Kalki - A Software-Defined IoT Security Platform
#  Copyright 2020 Carnegie Mellon University.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
#  [DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.
#  This Software includes and/or makes use of the following Third-Party Software subject to its own license:
#  1. Google Guava (https://github.com/google/guava) Copyright 2007 The Guava Authors.
#  2. JSON.simple (https://code.google.com/archive/p/json-simple/) Copyright 2006-2009 Yidong Fang, Chris Nokleberg.
#  3. JUnit (https://junit.org/junit5/docs/5.0.1/api/overview-summary.html) Copyright 2020 The JUnit Team.
#  4. Play Framework (https://www.playframework.com/) Copyright 2020 Lightbend Inc..
#  5. PostgreSQL (https://opensource.org/licenses/postgresql) Copyright 1996-2020 The PostgreSQL Global Development Group.
#  6. Jackson (https://github.com/FasterXML/jackson-core) Copyright 2013 FasterXML.
#  7. JSON (https://www.json.org/license.html) Copyright 2002 JSON.org.
#  8. Apache Commons (https://commons.apache.org/) Copyright 2004 The Apache Software Foundation.
#  9. RuleBook (https://github.com/deliveredtechnologies/rulebook/blob/develop/LICENSE.txt) Copyright 2020 Delivered Technologies.
#  10. SLF4J (http://www.slf4j.org/license.html) Copyright 2004-2017 QOS.ch.
#  11. Eclipse Jetty (https://www.eclipse.org/jetty/licenses.html) Copyright 1995-2020 Mort Bay Consulting Pty Ltd and others..
#  12. Mockito (https://github.com/mockito/mockito/wiki/License) Copyright 2007 Mockito contributors.
#  13. SubEtha SMTP (https://github.com/voodoodyne/subethasmtp) Copyright 2006-2007 SubEthaMail.org.
#  14. JSch - Java Secure Channel (http://www.jcraft.com/jsch/) Copyright 2002-2015 Atsuhiko Yamanaka, JCraft,Inc. .
#  15. ouimeaux (https://github.com/iancmcc/ouimeaux) Copyright 2014 Ian McCracken.
#  16. Flask (https://github.com/pallets/flask) Copyright 2010 Pallets.
#  17. Flask-RESTful (https://github.com/flask-restful/flask-restful) Copyright 2013 Twilio, Inc..
#  18. libvirt-python (https://github.com/libvirt/libvirt-python) Copyright 2016 RedHat, Fedora project.
#  19. Requests: HTTP for Humans (https://github.com/psf/requests) Copyright 2019 Kenneth Reitz.
#  20. netifaces (https://github.com/al45tair/netifaces) Copyright 2007-2018 Alastair Houghton.
#  21. ipaddress (https://github.com/phihag/ipaddress) Copyright 2001-2014 Python Software Foundation.
#  DM20-0543
#
#
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

    def handleTCPPacket(self, tcp_packet, ip_packet):
        try:
            http = HTTP(tcp_packet.data)
        except:
            return

        try:
            request_path = urlparse(http.uri).path

            # Strip out token
            match = api_uri_pattern.match(http.uri)

            # Check if the uri is just a request for username ("/api")
            if request_path == "/api":
                self.trackTokenRequest(ip_packet.src)
            elif match:
                token = match.group(1)
                self.trackAPIRequest(token, ip_packet.src)
            else:
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
            return

    def handleUDPPacket(self, ip_packet):
        # This handler does not process UDP packets; simply return
        return

    def trackAPIRequest(self, token, ip):
        # Get all unique token requests for the IP address
        if ip not in self.api_requests.keys():
            requests = Requests()
            self.api_requests[ip] = requests
        else:
            requests = self.api_requests[ip]
        
        # Determine if token has been used before
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
        if (current_time - self.last_log_time) > self.config["logging_timeout"]:
            msg = ("BRUTE_FORCE: IP address " +str(ip)+ " has attempted device api calls with " +str(self.config["max_attempts"]) +
                " different tokens within " +str(self.config["max_attempts_interval_secs"]) + " seconds")
            self.logger.warning(msg)
            self.last_log_time = current_time
            self.result.issues_found.append("BRUTE_FORCE")

    def logBruteForceToken(self, ip):
        current_time = time.time()
        if (current_time - self.last_log_time) > self.config["logging_timeout"]:
            msg = ("BRUTE_FORCE: IP address " +str(ip)+ " has attempted to get a token " +str(self.config["max_attempts"]) +
                " times within " +str(self.config["max_attempts_interval_secs"]) + " seconds")
            self.logger.warning(msg)
            self.last_log_time = current_time
            self.result.issues_found.append("BRUTE_FORCE")


class Requests:

    def __init__(self):
        self.attempt_times = []
        self.token_set = set()

    def addRequest(self, token, current_attempt_time):
        self.attempt_times.append({"token": token, "time": current_attempt_time})
        self.token_set.add(token)
