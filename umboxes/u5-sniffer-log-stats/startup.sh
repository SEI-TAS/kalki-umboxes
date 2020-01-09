#!/usr/bin/env bash

cd alerter
bash alerter.sh &

cd ..
cd sniffer
bash sniffer.sh
