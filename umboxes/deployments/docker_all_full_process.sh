#!/usr/bin/env bash

DEPLOYMENT="$1"

update_umbox() {
    local umbox_name="$1"

    echo "Updating ${umbox_name}"
    time bash build_umbox_image.sh ${umbox_name} ${DEPLOYMENT}
    echo "Finished updating ${umbox_name}"
}

echo "Updating all docker umboxes for deployment ${DEPLOYMENT}"

for DIR in ../standard/*/   # list directories with full path
do
    DIR=${DIR%*/}          # remove the trailing "/"
    UMBOX_NAME=${DIR##*/}  # remove all path before current directory
    update_umbox ${UMBOX_NAME}
done

echo "Finished updating all docker umboxes"
