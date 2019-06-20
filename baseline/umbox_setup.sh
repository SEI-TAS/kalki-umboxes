#!/usr/bin/env bash

# NOTE: this is only needed if behind a proxy.
PROXY="http://proxy.sei.cmu.edu:8080"
echo "Acquire::http::Proxy \"${PROXY}\";" | sudo tee /etc/apt/apt.conf
echo "export http_proxy=${PROXY}" >> $HOME/.profile
echo "export https_proxy=${PROXY}" >> $HOME/.profile
export http_proxy=${PROXY}
export https_proxy=${PROXY}

# Install Python, PIP and Pipenv
apt-get update
apt-get install -yqq python python-pip
pip install pipenv

# Make virtualenvs appear in current directory.
echo "export PIPENV_VENV_IN_PROJECT=\"enabled\"" >> $HOME/.profile
export PIPENV_VENV_IN_PROJECT="enabled"

# Setup Alerter
cd /home/vagrant/alerter
chmod ugo+x alerter.sh
pipenv install
cp alerter.service /etc/systemd/system/
systemctl enable alerter
systemctl start alerter
