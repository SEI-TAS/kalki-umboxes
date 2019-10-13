#!/usr/bin/env bash

SERVER=10.27.151.117
CAMERAPORT=80
PROXYPORT=9010
USER=kuser
PASS=kpass
export http_proxy='';

# Not authenticated.
curl -s -o /dev/null -w "Status: %{http_code}\n" http://${SERVER}:${CAMERAPORT}/Image.jpg

# Wrong credentials.
curl -s -o /dev/null -w "Status: %{http_code}\n" -u Wrong:Wrong http://${SERVER}:${PROXYPORT}/

# Appropriate credentials.
curl -s -o /dev/null -w "Status: %{http_code}\n" -u ${USER}:${PASS} http://${SERVER}:${PROXYPORT}/

# API call.
curl -s -o /dev/null -w "Status: %{http_code}\n" http://${SERVER}:${CAMERAPORT}/Image.jpg
