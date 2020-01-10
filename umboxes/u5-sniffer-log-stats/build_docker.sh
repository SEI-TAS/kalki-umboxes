#!/usr/bin/env bash

UMBOX_NAME=u5
PATH_TO_UMBOX=umboxes/u5-sniffer-log-stats

docker build -t ${UMBOX_NAME} --build-arg UMBOX_PATH=${PATH_TO_UMBOX} -f ${PATH_TO_UMBOX}/Dockerfile .
