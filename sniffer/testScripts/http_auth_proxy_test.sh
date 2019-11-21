#!/usr/bin/env bash

# Information configred in the auth proxy.
PROXY_PORT=9010
RIGHT_USER=kuser
RIGHT_PASS=kpass

# Action and IoT device info, get from command line or use defaults.
OPTION=${1:-API}
DEVICE_IP=${2:-'10.27.151.114'}
DEVICE_PORT=${3:-80}

echo "Action: ${OPTION}, IP: ${DEVICE_IP}, DEVICE PORT: ${DEVICE_PORT}"

# Disable proxy, if any.
export http_proxy='';

# Command line argument tells us what to do.
if [ "$OPTION" = "API" ]; then
    # API call.
    echo "Attempting API call to device and its port."
    curl -s -o /dev/null -w "Status: %{http_code}\n" http://${DEVICE_IP}:${DEVICE_PORT}/
elif [ "$OPTION" = "WRONG" ]; then
    # Wrong credentials.
    echo "Attempting incorrect authentication to proxy on port ${PROXY_PORT}"
    curl -s -o /dev/null -w "Status: %{http_code}\n" -u Wrong:Wrong http://${DEVICE_IP}:${PROXY_PORT}/
elif [ "$OPTION" = "RIGHT" ]; then
    # Appropriate credentials.
    echo "Attempting correct authentication to proxy on port ${PROXY_PORT}"
    curl -s -o /dev/null -w "Status: %{http_code}\n" -u ${RIGHT_USER}:${RIGHT_PASS} http://${DEVICE_IP}:${PROXY_PORT}/
else
    echo "Invalid option selected: ${OPTION}"
fi
