#!/usr/bin/env bash

UMBOX_FOLDER=${PWD##*/}

cp *_standalone.qcow2 ../../../kalki-umbox-controller/clone-image-server/images/${UMBOX_FOLDER}.qcow2
echo "Copied, deleting original"
rm -f *_standalone.qcow2
