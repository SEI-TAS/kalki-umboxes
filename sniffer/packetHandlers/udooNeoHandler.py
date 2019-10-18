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

        # Ignore compromise check for TCP for now.
        return

        # Only check for Compromise if it is in the config file
        if "COMPROMISE" in self.config["check_list"]:
            # Only consider packets coming from the IoT device, which means the source is the IoT subnet
            if (ip_packet.src.find(self.config["iot_subnet"]) > -1):
                # TCP traffic originating from the IoT device.  Only TCP traffic from port 22 is SSH traffic (thus valid)
                if tcp_packet.src_port != 22:
                    # TCP traffic that is definitely not coming from a SSH server port on the IoT device.  Count as compromise evidence
                    self.tcp_compromise_count += 1

                    # Check compromise threshold
                    if self.udp_compromise_count + self.tcp_compromise_count == self.config["compromise_threshold"]:
                        self.logCompromise(ip_packet.src)

        return

    def handleUDPPacket(self, ip_packet):
        # Only check for Compromise if it is in the config file
        if "COMPROMISE" in self.config["check_list"]:
            # Any UDP Packet originating from the UN IoT device is questionable; flagged for compromise
            if (ip_packet.src.find(self.config["iot_subnet"]) > -1):
                # Only check for traffic going to our defined external network
                if ip_packet.target.find("10.27.152") > -1:
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
        msg = ("COMPROMISE: Detected " + str(self.udp_compromise_count) + " invalid UDP packets and + " + str(self.tcp_compromise_count) + " invalid TCP packets from UN device at " + str(ip) + ", exceeding limit of " + str(self.config["compromise_threshold"]))
        self.logger.warning(msg)
        self.result.issues_found.append("COMPROMISE")
