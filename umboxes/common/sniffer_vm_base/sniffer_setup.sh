#!/usr/bin/env bash

SNIFFER_HOME=$1

# Python 3 and pipenv are assumed installed by Alerter setup (common).

# Setup Sniffer
cd ${SNIFFER_HOME}
pipenv install

# Set up service.
chmod ugo+x sniffer.sh
cp sniffer.service /etc/systemd/system/
systemctl enable sniffer
systemctl start sniffer
