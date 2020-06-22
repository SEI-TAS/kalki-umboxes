#!/bin/bash

while true; do
  grep -q '^1$' "/sys/class/net/eth0/carrier" &&
	  grep -q '^1$' "/sys/class/net/eth1/carrier" &&
	  grep -q '^1$' "/sys/class/net/eth2/carrier" &&
	  grep -q '^1$' "/sys/class/net/eth3/carrier" &&
	  break

  sleep 1
done
