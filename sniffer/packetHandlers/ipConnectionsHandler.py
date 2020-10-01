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
import time


class IpConnectionsHandler:

    def __init__(self, config, logger, result):
        self.config = config["ipConnections"]
        self.config["deviceIpAddress"] = config["deviceIpAddress"]
        #self.config["iot_subnet"] = config["iot_subnet"]
        #self.config["external_subnet"] = config["external_subnet"]
        self.logger = logger
        self.connections = {}
        self.last_log_time = 0
        self.result = result
        self.udp_compromise_count = 0
        self.tcp_compromise_count = 0

    def handleTCPPacket(self, tcp_packet, ip_packet):
        # Only check for Brute Force if it is in the config file
        if "BRUTE_FORCE" in self.config["check_list"]:
            self.trackConnection(tcp_packet, ip_packet.src)

        # Only check for Compromise if it is in the config file
        if "COMPROMISE" in self.config["check_list"] and self.config["compromise_tcp"] == "on":
            self.checkCompromise(ip_packet, tcp_packet.src_port)

        return

    def handleUDPPacket(self, ip_packet):
        # Only check for Compromise if it is in the config file
        if "COMPROMISE" in self.config["check_list"] and self.config["compromise_udp"] == "on":
            self.checkCompromise(ip_packet, None)

    def trackConnection(self, tcp_packet, ip):
        # Track all connection requests
        if tcp_packet.flag_syn == 1 and tcp_packet.flag_ack == 0:
            if ip not in self.connections.keys():
                connection_times = []
                self.connections[ip] = connection_times
            else:
                connection_times = self.connections[ip]

            current_attempt_time = time.time()
            connection_times.append(current_attempt_time)

            if len(connection_times) >= self.config["max_attempts"]:
                seconds_from_first_attempt = (current_attempt_time - connection_times[0])
                if seconds_from_first_attempt < self.config["max_attempts_interval_secs"]:
                    self.logBruteForce(ip)

                # If we've reached the max attempts, trim the first one and keep the other N-1 ones for future checks
                connection_times.pop(0)

    def checkCompromise(self, ip_packet, tcp_port):
        # Only consider packets coming from the IoT device
        if ip_packet.src.find(self.config["deviceIpAddress"]) > -1:
            # TCP traffic originating from the IoT device.  TCP traffic from designed ports is valid
            if tcp_port and tcp_port not in self.config["compromise_allowed_ports"]:
                # TCP traffic that is not coming from an allowed port on the IoT device.
                self.tcp_compromise_count += 1
            else:
                # All non-TCP traffic is counted as compromised as well.
                self.udp_compromise_count += 1

            # Check compromise threshold
            if self.udp_compromise_count + self.tcp_compromise_count == self.config["compromise_threshold"]:
                self.logCompromise(ip_packet.src)

    def logBruteForce(self, ip):
        current_time = time.time()
        if current_time - self.last_log_time > self.config["logging_timeout"]:
            msg = ("BRUTE_FORCE: IP address " +str(ip)+ " has started " +str(self.config["max_attempts"])+ 
                " TCP connections within " +str(self.config["max_attempts_interval_secs"])+ " seconds")
            self.logger.warning(msg)
            self.last_log_time = current_time
            self.result.issues_found.append("BRUTE_FORCE")

    def logCompromise(self, ip):
        msg = ("COMPROMISE: Detected " + str(self.udp_compromise_count) + " invalid UDP packets and + " + str(self.tcp_compromise_count) + " invalid TCP packets from device at " + str(ip) + ", exceeding limit of " + str(self.config["compromise_threshold"]))
        self.logger.warning(msg)
        self.result.issues_found.append("COMPROMISE")
