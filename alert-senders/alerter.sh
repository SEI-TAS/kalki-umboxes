#!/usr/bin/env bash
cd /home/umbox/alert-senders
pipenv run python -u /home/umbox/alert-senders/log_checker.py -f ../credential-sniffer/sniffer.log
