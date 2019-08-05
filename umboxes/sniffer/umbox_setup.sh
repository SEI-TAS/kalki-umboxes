#!/usr/bin/env bash

# Restart Alerter to use the new configuration.
systemctl restart alerter

# Setup Sniffer
cd /home/vagrant/sniffer
chmod ugo+x sniffer.sh
pipenv install
cp sniffer.service /etc/systemd/system/
systemctl enable sniffer
systemctl start sniffer
