#!/bin/bash

apt-get update
apt-get install -yqq squid3 apache2-utils ethtool

cp /home/vagrant/squid/squid.conf /etc/squid/squid.conf
cp /home/vagrant/squid/squid.service /etc/systemd/system

systemctl stop squid
systemctl enable squid
systemctl start squid


