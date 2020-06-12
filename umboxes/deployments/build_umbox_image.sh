#!/usr/bin/env bash

UMBOX_NAME="$1"
DEPLOYMENT="$2"
docker build \
  -t kalki-${DEPLOYMENT}/${UMBOX_NAME} \
  --build-arg UMBOX_IMAGE=$UMBOX_NAME \
  --build-arg DEPLOYMENT=$DEPLOYMENT \
  .
