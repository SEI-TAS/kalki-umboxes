#!/usr/bin/env bash

UMBOX_FOLDER=${PWD##*/}

# NOTE: assumes kalki umbox controller is installed in this folder. Change if different.
UMBOX_CONTROLLER_FOLDER=/home/local/SSDLAB/secheverria/kalki/kalki-umbox-controller
sudo cp *_standalone.qcow2 ${UMBOX_CONTROLLER_FOLDER}/clone-image-server/images/${UMBOX_FOLDER}.qcow2
echo "Copied, deleting original"
rm -f *_standalone.qcow2
