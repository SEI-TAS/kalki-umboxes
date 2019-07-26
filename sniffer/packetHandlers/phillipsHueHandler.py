class PhillipsHueHandler:

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def handlePacket(self, tcp_packet, ip_packet):
        print("handling phillips packet")
