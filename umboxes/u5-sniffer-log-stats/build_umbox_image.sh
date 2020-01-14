#!/usr/bin/env bash

UMBOX_NAME=${PWD##*/}
docker build -t ${UMBOX_NAME} .
