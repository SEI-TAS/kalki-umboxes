#!/usr/bin/env bash
# NOTE: execute script with sudo and at folder where Vagrant folder is.

UMBOX_FOLDER=${PWD##*/}
UMBOX_DEPENDENT_IMAGE=/var/lib/libvirt/images/${UMBOX_FOLDER}_default.img
echo "Creating standalone image for file ${UMBOX_DEPENDENT_IMAGE}"

# Name for the standalone image.
UMBOX_STANDALONE_IMAGE=${UMBOX_DEPENDENT_IMAGE}_standalone.qcow2

# Name for tmp image to avoid rebasing original.
UMBOX_DEPENDENT_IMAGE_TMP_COPY=${UMBOX_STANDALONE_IMAGE}.tmp

# Get base image path.
BASE_IMAGE=qemu-img info ${UMBOX_DEPENDENT_IMAGE} | grep "backing file: " | sed 's/^.*: //'
echo "Backing file found: ${BASE_IMAGE}"

# Copy base and dependent images to avoid messing up with originals.
echo "Copying base and dependent image files"
cp ${BASE_IMAGE} ${UMBOX_STANDALONE_IMAGE}
cp ${UMBOX_DEPENDENT_IMAGE} ${UMBOX_DEPENDENT_IMAGE_TMP_COPY}

# Modify dependent image to point to new copy of backing file.
echo "Rebasing dependent file"
qemu-img rebase -b ${UMBOX_STANDALONE_IMAGE} ${UMBOX_DEPENDENT_IMAGE_TMP_COPY}

# Merge dependent image into copy of backing file.
echo "Merging files"
qemu-img commit ${UMBOX_DEPENDENT_IMAGE_TMP_COPY}

# Make the new image readable but not writable.
chmod ugo+r ${UMBOX_STANDALONE_IMAGE}
chmod ugo-w ${UMBOX_STANDALONE_IMAGE}

# Remov temporary dependent image.
rm ${UMBOX_DEPENDENT_IMAGE_TMP_COPY}

echo "Done"
