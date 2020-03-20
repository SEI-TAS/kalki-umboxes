#!/bin/bash

# Link incoming and outgoing NICs by a virtual bridge.
brctl addbr bridge0
ifconfig eth1 down
ifconfig eth2 down
brctl addif bridge0 eth1 eth2
ifconfig eth1 up
ifconfig eth2 up
ifconfig bridge0 up

# Enable IPv4 forwarding.
echo 1 > /proc/sys/net/ipv4/ip_forward

# Maximum number of connections
if [ -z "$MAX_CONN" ]; then
    MAX_CONN="5"
fi

# Grouping for determining maximum number of connections
# \32 == per host
# \24 == per subnet
if [ -z "$CONN_MASK" ]; then
    CONN_MASK="32"
fi

# Maximum bandwidth (defaults to packets/sec)
if [ -z "$MAX_RATE" ]; then
    MAX_RATE="5000"
fi

# Grouping for determining maximum bandwidth group
if [ -z "$MODE" ]; then
    MODE="srcip,srcport,dstip,dstport"
fi

# Limit number of simultaneous connections: drops above $MAX_CONN
iptables -A FORWARD -i eth1 -p tcp -m tcp --tcp-flags FIN,SYN,RST,ACK SYN -m connlimit --connlimit-above $MAX_CONN --connlimit-mask $CONN_MASK --connlimit-saddr -j REJECT --reject-with tcp-reset
iptables -A FORWARD -i eth2 -p tcp -m tcp --tcp-flags FIN,SYN,RST,ACK SYN -m connlimit --connlimit-above $MAX_CONN --connlimit-mask $CONN_MASK --connlimit-saddr -j REJECT --reject-with tcp-reset
# Limit the throughput (in either pkts/sec or Bytes/sec, for granularity/group desired--src&dst, only dst, dst&dstport, etc; specified in --hashlimit-mode). --hashlimit-above X/time (or Xb/time for Bytes, does not allow modifiers such as K or M)
iptables -A FORWARD -i eth1 -m hashlimit --hashlimit-above "$MAX_RATE"/sec --hashlimit-mode $MODE --hashlimit-name foo -j DROP
iptables -A FORWARD -i eth2 -m hashlimit --hashlimit-above "$MAX_RATE"/sec --hashlimit-mode $MODE --hashlimit-name foo -j DROP

#spin
/bin/bash
