#!/usr/bin/env bash

ALERTER_HOME=$1

# Install Python, PIP and Pipenv
apt-get update
apt-get install -yqq python3 python3-pip
pip3 install pipenv
pip3 install setuptools --upgrade

# Make virtualenvs appear in current directory.
echo "export PIPENV_VENV_IN_PROJECT=\"enabled\"" >> $HOME/.profile
export PIPENV_VENV_IN_PROJECT="enabled"

# Setup Alerter
cd ${ALERTER_HOME}
pipenv install

# Setup service.
chmod ugo+x alerter.sh
cp alerter.service /etc/systemd/system/
systemctl enable alerter
systemctl start alerter
