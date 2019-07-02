#!/usr/bin/env bash

# Setup DNS resolution. This is needed to avoid issues with proxies when resolving names.
# This IP is the gateway/DNS of the default libvirt network we are using.
echo "nameserver 192.168.121.1" > /etc/resolv.conf

# NOTE: this is only needed if behind a proxy.
PROXY="http://proxy.sei.cmu.edu:8080"
echo "Acquire::http::Proxy \"${PROXY}\";" | sudo tee /etc/apt/apt.conf
echo "export http_proxy=${PROXY}" >> $HOME/.profile
echo "export https_proxy=${PROXY}" >> $HOME/.profile

