#!/usr/bin/env bash

UMBOX_NAME=$1
PATH_TO_UMBOX=$2

docker build -t ${UMBOX_NAME} --build-arg UMBOX_PATH=${PATH_TO_UMBOX} -f ../../umboxes/sniffer_docker/Dockerfile ../../
