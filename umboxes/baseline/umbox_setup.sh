#!/usr/bin/env bash

# Decrease DHCP timeout.
sed -i 's/timeout 300/timeout 15/g' /etc/dhcp/dhclient.conf
