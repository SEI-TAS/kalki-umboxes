FROM openjdk:8

ARG UMBOX_PATH

# Setup Alerter.
COPY ./alerter /alerter
COPY ./umboxes/sniffer_docker/config_alerter.json /alerter/config.json
COPY ./umboxes/sniffer_docker/alerter_setup.sh /
RUN ["bash", "alerter_setup.sh"]

# Setup Sniffer.
COPY ./sniffer /sniffer
COPY $UMBOX_PATH/config.json /sniffer/config.json
COPY ./umboxes/sniffer_docker/sniffer_setup.sh /
RUN ["bash", "sniffer_setup.sh"]

# Start up everything.
COPY ./umboxes/sniffer_docker/startup.sh /startup.sh
ENTRYPOINT ["bash", "startup.sh"]
