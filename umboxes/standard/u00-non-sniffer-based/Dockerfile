FROM kalki/alerter

# Setup Sniffer.
COPY /sniffer /sniffer
WORKDIR /sniffer
RUN ["bash", "sniffer_setup.sh"]

# Copy Sniffer-specific Alerter config.
COPY ./config_alerter.json /alerter/config.json

# Start up everything.
COPY /startup.sh /startup.sh
WORKDIR /
ENTRYPOINT ["bash", "startup.sh"]
