#!/bin/bash

# Install required tools.
apt-get update
apt-get install -yqq net-tools bridge-utils iproute2 iptables arptables tcpdump

# Setup service to set config each time machine is started.
cp /home/vagrant/antidos/antidos.service /etc/systemd/system
systemctl enable antidos
systemctl start antidos
