#!/usr/bin/env bash

# Setup Sniffer
cd /home/vagrant/credential-sniffer
chmod ugo+x sniffer.sh
pipenv install
cp sniffer.service /etc/systemd/system/
systemctl enable sniffer
systemctl start sniffer
