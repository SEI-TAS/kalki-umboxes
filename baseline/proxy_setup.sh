#!/usr/bin/env bash

# NOTE: this is only needed if behind a proxy.
PROXY="http://proxy.sei.cmu.edu:8080"
echo "Acquire::http::Proxy \"${PROXY}\";" | sudo tee /etc/apt/apt.conf
echo "export http_proxy=${PROXY}" >> $HOME/.profile
echo "export https_proxy=${PROXY}" >> $HOME/.profile

