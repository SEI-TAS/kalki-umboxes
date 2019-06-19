#!/usr/bin/env bash
apt-get update
apt-get install -yqq python python-pip
pip install pipenv

cd /home/umbox/alerter
pipenv install
cp alerter.service /etc/systemd/system/

cd /home/umbox/credential-sniffer
pipenv install
cp sniffer.service /etc/systemd/system/