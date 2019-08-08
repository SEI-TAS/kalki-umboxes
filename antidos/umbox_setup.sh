#!/bin/bash

apt-get update
apt-get install -yqq net-tools bridge-utils iproute2 iptables arptables tcpdump

echo 1 > /proc/sys/net/ipv4/ip_forward

cp /home/vagrant/antidos.service /etc/systemd/system

systemctl enable antidos
systemctl start antidos


