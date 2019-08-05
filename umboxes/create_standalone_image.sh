#!/usr/bin/env bash
# Use absolute paths or execute script at folder where umbox image is.

BASE_IMAGE=$1
UMBOX_CHILD_IMAGE=$2
UMBOX_FULL_IMAGE=$3

cp ${BASE_IMAGE} ${UMBOX_FULL_IMAGE}
qemu-img rebase -b ${UMBOX_FULL_IMAGE} ${UMBOX_CHILD_IMAGE}
qemu-img commit ${UMBOX_CHILD_IMAGE}
chmod ugo+r ${UMBOX_FULL_IMAGE}
chmod ugo-w ${UMBOX_FULL_IMAGE}