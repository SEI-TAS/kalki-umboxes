#!/usr/bin/env bash

CAMERA=10.27.151.202  # WiFi AP IP since camera won't return to another private LAN.
CAMERAPORT=80
PROXYPORT=9010
export http_proxy='';

# Try several times
for i in {1..10}
do
    # bash generate random 16 character alphanumeric string (upper and lowercase)
    NEW_PASS="pass${i}"

    curl -s -o /dev/null -w "Status: %{http_code}\n" -u user1:${NEW_PASS} http://${CAMERA}:${CAMERAPORT}/
    sleep 0.5
done
