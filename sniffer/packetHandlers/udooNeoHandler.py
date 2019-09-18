import time
import traceback

class UdooNeoHandler:

    def __init__(self, config, logger, result):
        self.config = config["udooNeo"]
        self.logger = logger
        self.connections = {}
        self.last_log_time = 0
        self.result = result


    def handlePacket(self, tcp_packet, ip_packet):
        if tcp_packet.flag_syn == 1 and tcp_packet.flag_ack == 0:
            self.trackConnection(ip_packet.src)
        
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
