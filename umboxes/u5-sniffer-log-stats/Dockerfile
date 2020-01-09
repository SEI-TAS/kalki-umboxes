FROM openjdk:8

# Setup Alerter.
COPY ../../alerter /alerter
COPY config_alerter.json /alerter/config.json
RUN ./alerter_setup.sh

# Setup Sniffer.
COPY ../../sniffer /sniffer
COPY config.json /sniffer/config.json
RUN ./sniffer_setup.sh

# Start up everything.
COPY startup.sh /startup.sh
ENTRYPOINT ["bash", "startup.sh"]
