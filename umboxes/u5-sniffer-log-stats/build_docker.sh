#!/usr/bin/env bash

UMBOX_NAME=u5
PATH_TO_UMBOX=umboxes/u5-sniffer-log-stats

bash ../sniffer_docker/build_docker_image.sh ${UMBOX_NAME} ${PATH_TO_UMBOX}
