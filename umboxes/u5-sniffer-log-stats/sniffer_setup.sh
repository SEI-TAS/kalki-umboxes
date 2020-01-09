#!/usr/bin/env bash

# Python 3 and pipenv are assumed installed by Alerter setup (common).
# Setup Sniffer
cd /sniffer
export PIPENV_VENV_IN_PROJECT="enabled"
pipenv install
