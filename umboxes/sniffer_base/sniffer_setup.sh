#!/usr/bin/env bash

SNIFFER_HOME=$1

# Install Python 3.6.
sudo -E add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.6

# Setup Sniffer
cd ${SNIFFER_HOME}
chmod ugo+x sniffer.sh
pipenv install
cp sniffer.service /etc/systemd/system/
systemctl enable sniffer
systemctl start sniffer
