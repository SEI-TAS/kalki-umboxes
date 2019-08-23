#!/usr/bin/env bash

# Decrease DHCP timeout.
sed -i 's/timeout 300/timeout 15/g' /etc/dhcp/dhclient.conf

# Setup network interfaces.
echo -e "auto lo\niface lo inet loopback"  > /etc/network/interfaces
echo -e "auto eth0\niface eth0 inet dhcp" >> /etc/network/interfaces
echo -e "auto eth1\niface eth1 inet dhcp" >> /etc/network/interfaces
echo -e "auto eth2\niface eth2 inet dhcp" >> /etc/network/interfaces
echo -e "auto eth3\niface eth3 inet dhcp" >> /etc/network/interfaces
