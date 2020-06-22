#!/usr/bin/env bash

IP_ADDRESS=$1

# Clear proxy vars to avoid issues communicating with Controller.
export http_proxy=""
export https_proxy=""
export HTTP_PROXY=""
export HTTPS_PROXY=""

cd alerter
python3 -u alerter.py 2>&1 | tee -a alerter.log &

cd ..
cd sniffer
echo "{\"deviceIpAddress\": \"${IP_ADDRESS}\"}" > device_info.json
python3 -u sniffer.py 2>&1 | tee -a sniffer.log &

# Dummy proxy to keep container running, while allowing to restart alerter or sniffer for debugginng.
tail -f sniffer.sh
