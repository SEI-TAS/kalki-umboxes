FROM python:3.5

# Setup Alerter.
COPY ./alerter /alerter
WORKDIR /alerter
RUN ["bash", "alerter_setup.sh"]
WORKDIR /

# Wait for required eth interfaces
COPY ./umboxes/common/alerter_docker/iface_check /iface_check

