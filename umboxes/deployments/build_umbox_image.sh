#!/usr/bin/env bash

UMBOX_NAME="$1"
DEPLOYMENT="$2"
docker build \
  -t ${UMBOX_NAME}-${DEPLOYMENT} \
  --build-arg UMBOX_IMAGE=$UMBOX_NAME \
  --build-arg DEPLOYMENT=$DEPLOYMENT \
  .
