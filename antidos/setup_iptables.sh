#!/bin/bash

brctl addbr bridge0
ifconfig eth2 down
ifconfig eth3 down
brctl addif bridge0 eth2 eth3
ifconfig eth2 up
ifconfig eth3 up
ifconfig bridge0 up

# Maximum number of connections
if [ -z "$MAX_CONN" ]; then
    MAX_CONN="10"
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


#Limit number of simultaneous connections: drops above $MAX_CONN
iptables -A FORWARD -p tcp -m tcp --tcp-flags FIN,SYN,RST,ACK SYN -m connlimit --connlimit-above $MAX_CONN --connlimit-mask $CONN_MASK --connlimit-saddr -j REJECT --reject-with tcp-reset
#Limit the throughput (in either pkts/sec or Bytes/sec, for granularity/group desired--src&dst, only dst, dst&dstport, etc; specified in --hashlimit-mode). --hashlimit-above X/time (or Xb/time for Bytes, does not allow modifiers such as K or M)
iptables -A FORWARD -m hashlimit --hashlimit-above "$MAX_RATE"/sec --hashlimit-mode $MODE --hashlimit-name foo -j DROP

