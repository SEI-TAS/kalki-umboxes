#!/bin/bash

sudo cp snort/snort.conf /etc/snort/snort.conf
sudo cp snort/local.rules /etc/snort/rules/local.rules

sudo systemctl restart snort



