#!/usr/bin/env bash

SNIFFER_HOME=$1

# Setup HTTP Server
cd ${SNIFFER_HOME}
chmod ugo+x httpserver.sh
cp httpserver.service /etc/systemd/system/
systemctl enable httpserver
systemctl start httpserver
