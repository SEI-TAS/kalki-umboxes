FROM kalki/alerter

# Install required tools.
RUN apt-get update
RUN apt-get install -yqq net-tools bridge-utils iproute2 iptables arptables tcpdump

# Setup rules.
COPY ./umboxes/standard/u1-antidos/setup_iptables.sh /setup_iptables.sh

ENTRYPOINT ["bash", "setup_iptables.sh"]
