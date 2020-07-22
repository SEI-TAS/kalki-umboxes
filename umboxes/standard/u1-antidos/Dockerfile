FROM kalki/alerter

# Install required tools.
RUN apk --no-cache add bash net-tools bridge-utils iproute2 iptables tcpdump

# Setup rules.
COPY ./setup_iptables.sh /setup_iptables.sh

ENTRYPOINT ["bash", "setup_iptables.sh"]
