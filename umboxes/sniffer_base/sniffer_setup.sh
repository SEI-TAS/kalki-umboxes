#!/usr/bin/env bash

# Install Python 3.6.
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.6

# Setup Sniffer
cd /home/vagrant/sniffer
chmod ugo+x sniffer.sh
pipenv install
cp sniffer.service /etc/systemd/system/
systemctl enable sniffer
systemctl start sniffer
