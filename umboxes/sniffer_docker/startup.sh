#!/usr/bin/env bash

# Clear proxy vars to avoid issues communicating with Controller.
export http_proxy=""
export https_proxy=""
export HTTP_PROXY=""
export HTTPS_PROXY=""

cd alerter
bash alerter.sh 2>&1 | tee -a alerter.log &

cd ..
cd sniffer
bash sniffer.sh 2>&1 | tee -a sniffer.log
