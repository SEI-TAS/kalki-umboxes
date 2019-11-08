#!/usr/bin/env bash

DEVICE_IP=10.27.151.114
DEVICE_PORT=80
PROXY_PORT=9010
USER=kuser
PASS=kpass
export http_proxy='';

OPTION=$1

if ["$OPTION" == "API"]; then
    # API call.
    curl -s -o /dev/null -w "Status: %{http_code}\n" http://${DEVICE_IP}:${DEVICE_PORT}/
elif ["$OPTION" == "WRONG"]; then
    # Wrong credentials.
    curl -s -o /dev/null -w "Status: %{http_code}\n" -u Wrong:Wrong http://${DEVICE_IP}:${PROXY_PORT}/
elif ["$OPTION" == "RIGHT"]; then
    # Appropriate credentials.
    curl -s -o /dev/null -w "Status: %{http_code}\n" -u ${USER}:${PASS} http://${DEVICE_IP}:${PROXY_PORT}/
fi
