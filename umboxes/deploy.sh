#!/usr/bin/env bash

UMBOX_FOLDER=${PWD##*/}

sudo cp *_standalone.qcow2 /home/local/SSDLAB/secheverria/kalki/kalki-umbox-controller/clone-image-server/images/${UMBOX_FOLDER}.qcow2
echo "Copied, deleting original"
rm -f *_standalone.qcow2
