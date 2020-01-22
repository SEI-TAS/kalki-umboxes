#!/usr/bin/env bash

UMBOX_NAME=${PWD##*/}
docker build -t ${UMBOX_NAME} -f ../sniffer_docker/Dockerfile.umbox .
