#!/usr/bin/env bash

UMBOX_NAME="${1}"
DEPLOYMENT="${2}"
docker build -t ${UMBOX_NAME}-${DEPLOYMENT} -ARGS=<TODO> .
