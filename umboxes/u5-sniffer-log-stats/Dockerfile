FROM openjdk:8

ARG UMBOX_PATH

# Setup Alerter.
COPY ./alerter /alerter
COPY $UMBOX_PATH/config_alerter.json /alerter/config.json
RUN ./alerter_setup.sh

# Setup Sniffer.
COPY ./sniffer /sniffer
COPY $UMBOX_PATH/config.json /sniffer/config.json
RUN ./sniffer_setup.sh

# Start up everything.
COPY $UMBOX_PATH/startup.sh /startup.sh
ENTRYPOINT ["bash", "startup.sh"]
