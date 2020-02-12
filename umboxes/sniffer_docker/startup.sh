#!/usr/bin/env bash

IP_ADDRESS=$1

# Clear proxy vars to avoid issues communicating with Controller.
export http_proxy=""
export https_proxy=""
export HTTP_PROXY=""
export HTTPS_PROXY=""

cd alerter
bash alerter.sh 2>&1 | tee -a alerter.log &

cd ..
cd sniffer
echo "{\"deviceIpAddress\": \"${IP_ADDRESS}\"}" > device_info.json
bash sniffer.sh 2>&1 | tee -a sniffer.log &
tail -f sniffer.sh
