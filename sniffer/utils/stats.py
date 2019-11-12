import time


class PacketStats:

    def __init__(self):
        self.packet_count = 0
        self.tcp_count = 0
        self.udp_count = 0
        self.other_count = 0


class StatLogger:
    # Global stats map
    logger = None
    stat_interval = 0
    packet_stats_total = None
    packet_stats_senders = None
    packet_stats_targets = None
    packet_stats_last_log_time = None

    def __init__(self, logger, log_interval):
        self.logger = logger
        self.log_interval = log_interval

        self.packet_stats_total = PacketStats()
        self.packet_stats_last_log_time = time.time()
        self.packet_stats_senders = {}
        self.packet_stats_targets = {}

    def log_packet_statistics(self, ip_packet):
        # Log the current packet to the total stats
        self.packet_stats_total.packet_count += 1

        if ip_packet.proto == 6:
            self.packet_stats_total.tcp_count += 1
        elif ip_packet.proto == 17:
            self.packet_stats_total.udp_count += 1
        else:
            self.packet_stats_total.other_count += 1

        # Now log based on Senders
        if ip_packet.src not in self.packet_stats_senders:
            new_sender = PacketStats()
            self.packet_stats_senders[ip_packet.src] = new_sender

        self.packet_stats_senders[ip_packet.src].packet_count += 1
        if ip_packet.proto == 6:
            self.packet_stats_senders[ip_packet.src].tcp_count += 1
        elif ip_packet.proto == 17:
            self.packet_stats_senders[ip_packet.src].udp_count += 1
        else:
            self.packet_stats_senders[ip_packet.src].other_count += 1

        # Now log based on Receivers
        if ip_packet.target not in self.packet_stats_targets:
            new_target = PacketStats()
            self.packet_stats_targets[ip_packet.target] = new_target

        self.packet_stats_targets[ip_packet.target].packet_count += 1
        if ip_packet.proto == 6:
            self.packet_stats_targets[ip_packet.target].tcp_count += 1
        elif ip_packet.proto == 17:
            self.packet_stats_targets[ip_packet.target].udp_count += 1
        else:
            self.packet_stats_targets[ip_packet.target].other_count += 1

        # Now log based on timer
        if time.time() - self.packet_stats_last_log_time > self.log_interval:
            msg = "LOG_INFO: Packet stats total: {} tcp: {} udp: {} other: {}".format(self.packet_stats_total.packet_count,
                                                                                      self.packet_stats_total.tcp_count,
                                                                                      self.packet_stats_total.udp_count,
                                                                                      self.packet_stats_total.other_count)
            self.logger.warning(msg)
            for sender_ip in self.packet_stats_senders:
                msg = "LOG_INFO: Packets sent from {} stats total: {} tcp: {} udp: {} other: {}".format(sender_ip,
                                                                                                        self.packet_stats_total.packet_count,
                                                                                                        self.packet_stats_total.tcp_count,
                                                                                                        self.packet_stats_total.udp_count,
                                                                                                        self.packet_stats_total.other_count)
                self.logger.warning(msg)
            for target_ip in self.packet_stats_targets:
                msg = "LOG_INFO: Packets sent to {} stats total: {} tcp: {} udp: {} other: {}".format(target_ip,
                                                                                                      self.packet_stats_total.packet_count,
                                                                                                      self.packet_stats_total.tcp_count,
                                                                                                      self.packet_stats_total.udp_count,
                                                                                                      self.packet_stats_total.other_count)
                self.logger.warning(msg)

            self.packet_stats_last_log_time = time.time()
