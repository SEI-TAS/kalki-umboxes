#!/usr/bin/env bash

CAMERA=10.27.151.117
CAMERAPORT=80
PROXYPORT=9010
USER=kuser
PASS=kpass
export http_proxy='';

# Not authenticated.
curl -s -o /dev/null -w "Status: %{http_code}\n" http://${CAMERA}:${CAMERAPORT}/Image.jpg

# Wrong credentials.
curl -s -o /dev/null -w "Status: %{http_code}\n" -u Wrong:Wrong http://${CAMERA}:${PROXYPORT}/

# Appropriate credentials.
curl -s -o /dev/null -w "Status: %{http_code}\n" -u ${USER}:${PASS} http://${CAMERA}:${PROXYPORT}/

# API call.
curl -s -o /dev/null -w "Status: %{http_code}\n" http://${CAMERA}:${CAMERAPORT}/Image.jpg