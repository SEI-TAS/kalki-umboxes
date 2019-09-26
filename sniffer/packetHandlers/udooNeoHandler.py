import time
import traceback

class UdooNeoHandler:

    def __init__(self, config, logger, result):
        self.config = config["udooNeo"]
        self.logger = logger
        self.connections = {}
        self.last_log_time = 0
        self.result = result
        self.udp_compromise_count = 0
        self.tcp_compromise_count = 0

    def handleTCPPacket(self, tcp_packet, ip_packet):
        # Track all connection requests
        if tcp_packet.flag_syn == 1 and tcp_packet.flag_ack == 0:
            self.trackConnection(ip_packet.src)

        # Only check for Compromise if it is in the config file
        if "COMPROMISE" in self.config["check_list"]:
            # If the TCP packet is being sent TO port 22, TO the IoT device, it is part of an ssh connection; ignore
            if tcp_packet.dest_port == 22 and (self.config["iot_subnet"].find(ip_packet.target) > -1):
                # Part of an client to server SSH connection communication; ignore
                pass
            # If the TCP packet is being sent FROM port 22, FROM the IoT device, it is part of an ssh connection; ignore
            elif tcp_packet.src_port == 22 and (self.config["iot_subnet"].find(ip_packet.src) > -1):
                # Part of a server to client SSH connection communication; ignore
                pass
            else:
                # In all other cases, this TCP traffic is not part of a TCP SSH session where the IoT device is the server; therefore log as compromise
                self.tcp_compromise_count += 1

                # Check compromise threshold
                if self.udp_compromise_count + self.tcp_compromise_count == self.config["compromise_threshold"]:
                    self.logCompromise(ip_packet.src)

        return

    def handleUDPPacket(self, ip_packet):
        # Only check for Compromise if it is in the config file
        if "COMPROMISE" in self.config["check_list"]:
            # Any UDP Packet originating from the UN IoT device is questionable; flagged for compromise
            if (self.config["iot_subnet"].find(ip_packet.src) > -1):
                self.udp_compromise_count += 1

                # Check compromise threshold
                if self.udp_compromise_count + self.tcp_compromise_count == self.config["compromise_threshold"]:
                    self.logCompromise(ip_packet.src)
        return

    def trackConnection(self, ip):
        if ip not in self.connections.keys():
            connection_times = []
            self.connections[ip] = connection_times
        else:
            connection_times = self.connections[ip]
        
        current_attempt_time = time.time()
        connection_times.append(current_attempt_time)


        if len(connection_times) >= self.config["max_attempts"]:
            seconds_from_first_attempt = (current_attempt_time - connection_times[0])

            # Only check for Brute Force if it is in the config file
            if "BRUTE_FORCE" in self.config["check_list"]:
                if seconds_from_first_attempt < self.config["max_attempts_interval_secs"]:
                    self.logBruteForce(ip)
                
            # If we've reached the max attempts, trim the first one and keep the other N-1 ones for future checks
            connection_times.pop(0)


    def logBruteForce(self, ip):
        current_time = time.time()
        if current_time - self.last_log_time > self.config["logging_timeout"]:
            msg = ("BRUTE_FORCE: IP address " +str(ip)+ " has started " +str(self.config["max_attempts"])+ 
                " TCP connections within " +str(self.config["max_attempts_interval_secs"])+ " seconds")
            self.logger.warning(msg)
            self.last_log_time = current_time
            self.result.issues_found.append("BRUTE_FORCE")

    def logCompromise(self, ip):
        msg = ("COMPROMISE: Detected " + self.udp_compromise_count + " invalid UDP packets and + " + self.tcp_compromise_count + " invalid TCP packets from UN device at " + str(ip) + ", exceeding limit of " + self.config["compromise_threshold"])
        self.logger.warning(msg)
        self.result.issues_found.append("COMPROMISE")
