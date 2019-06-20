#!/usr/bin/env bash

# NOTE: this is only needed if behind a proxy.
PROXY="http://proxy.sei.cmu.edu:8080"
echo "Acquire::http::Proxy \"${PROXY}\";" | sudo tee /etc/apt/apt.conf
export http_proxy=${PROXY}
export https_proxy=${PROXY}

apt-get update
#apt-get install -yqq python
apt-get install -yqq python-pip
pip install pipenv

# Make virtualenvs appear in current directory.
export PIPENV_VENV_IN_PROJECT="enabled"

# Setup Alerter
cd /home/vagrant/alerter
pipenv install
cp alerter.service /etc/systemd/system/
systemctl enable alerter
systemctl start alerter

# Setup Credential-Sniffer
cd /home/vagrant/credential-sniffer
pipenv install
cp sniffer.service /etc/systemd/system/
systemctl enable sniffer
systemctl start sniffer
