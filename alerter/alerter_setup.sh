#!/usr/bin/env bash

# Install Python, PIP and Pipenv
apt-get update
apt-get install -yqq python3 python3-pip
pip3 install pipenv

# Make virtualenvs appear in current directory.
echo "export PIPENV_VENV_IN_PROJECT=\"enabled\"" >> $HOME/.profile

# Setup Alerter
export PIPENV_VENV_IN_PROJECT="enabled"
pipenv install
