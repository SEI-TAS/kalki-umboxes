#!/usr/bin/env bash

cd alerter
bash alerter.sh 2>&1 | tee -a alerter.log &

cd ..
cd sniffer
bash sniffer.sh 2>&1 | tee -a sniffer.log
