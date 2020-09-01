#!/usr/bin/env bash

DEVICE_IP=10.27.151.114
PROXY_PORT=80
export http_proxy='';

# Try several times
for i in {1..10}
do
    # bash generate random 16 character alphanumeric string (upper and lowercase)
    NEW_PASS="pass${i}"

    curl -s -o /dev/null -w "Status: %{http_code}\n" -u user1:${NEW_PASS} http://${DEVICE_IP}:${PROXY_PORT}/
    sleep 0.5
done
