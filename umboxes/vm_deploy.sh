#!/usr/bin/env bash

# NOTE: assumes kalki umbox controller is installed in this folder. Change if different.
UMBOX_IMAGES_FOLDER=/home/local/SSDLAB/secheverria/kalki/kalki-umbox-controller/clone-image-server/images

UMBOX_NAME=${PWD##*/}
sudo cp *_standalone.qcow2 ${UMBOX_IMAGES_FOLDER}/${UMBOX_NAME}.qcow2
echo "Copied, deleting original"
rm -f *_standalone.qcow2
