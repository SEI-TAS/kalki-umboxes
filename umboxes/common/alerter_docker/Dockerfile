FROM python:3.5

# Wait for required eth interfaces
COPY ./iface_check /iface_check
RUN ["bash", "/iface_check/wait_on_ifaces.sh"]
# Setup Alerter.
COPY ./alerter /alerter
WORKDIR /alerter
RUN ["bash", "alerter_setup.sh"]
WORKDIR /
