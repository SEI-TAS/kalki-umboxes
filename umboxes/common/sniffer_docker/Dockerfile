FROM kalki/alerter

# Setup Sniffer.
COPY ./sniffer /sniffer
WORKDIR /sniffer

# Install packages, temporarily installing GCC and deps.
RUN apk --no-cache add build-base && \
    pipenv install --system --deploy --ignore-pipfile && \
    apk del build-base

# Copy Sniffer-specific Alerter config.
COPY ./umboxes/common/sniffer_docker/config_alerter.json /alerter/config.json

# Start up everything.
COPY ./umboxes/common/sniffer_docker/startup.sh /startup.sh
WORKDIR /
ENTRYPOINT ["bash", "startup.sh"]
