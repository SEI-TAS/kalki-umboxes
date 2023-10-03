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


class PacketStats:

    def __init__(self):
        self.packet_count = 0
        self.tcp_count = 0
        self.udp_count = 0
        self.other_count = 0


class StatLogger:
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
