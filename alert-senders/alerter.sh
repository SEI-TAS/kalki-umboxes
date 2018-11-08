#!/usr/bin/env bash
cd /home/umbox/alert-senders
python -u /home/umbox/alert-senders/log_checker.py -f ../credential-sniffer/sniffer.log -s 127.0.0.1
