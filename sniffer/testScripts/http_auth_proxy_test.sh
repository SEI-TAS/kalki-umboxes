#!/usr/bin/env bash

# Information configred in the auth proxy.
PROXY_PORT=9010
RIGHT_USER=kuser
RIGHT_PASS=kpass

# Action and IoT device info, get from command line or use defaults.
OPTION=${1:-API}
DEVICE_IP=${2:-'10.27.151.114'}
DEVICE_PORT=${3:-80}

# Disable proxy, if any.
export http_proxy='';

# Command line argument tells us what to do.
if [ "$OPTION" = "API" ]; then
    # API call.
    curl -s -o /dev/null -w "Status: %{http_code}\n" http://${DEVICE_IP}:${DEVICE_PORT}/
elif [ "$OPTION" = "WRONG" ]; then
    # Wrong credentials.
    curl -s -o /dev/null -w "Status: %{http_code}\n" -u Wrong:Wrong http://${DEVICE_IP}:${PROXY_PORT}/
elif [ "$OPTION" = "RIGHT" ]; then
    # Appropriate credentials.
    curl -s -o /dev/null -w "Status: %{http_code}\n" -u ${RIGHT_USER}:${RIGHT_PASS} http://${DEVICE_IP}:${PROXY_PORT}/
fi
