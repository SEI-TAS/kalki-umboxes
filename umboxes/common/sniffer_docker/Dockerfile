FROM kalki/alerter

# For debugging.
RUN apt-get update
RUN apt-get install nano

# Setup Sniffer.
COPY ./sniffer /sniffer
WORKDIR /sniffer
RUN ["bash", "sniffer_setup.sh"]

# Copy Sniffer-specific Alerter config.
COPY ./umboxes/common/sniffer_docker/config_alerter.json /alerter/config.json

# Start up everything.
COPY ./umboxes/common/sniffer_docker/startup.sh /startup.sh
WORKDIR /
ENTRYPOINT ["bash", "startup.sh"]
