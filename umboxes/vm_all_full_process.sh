#!/usr/bin/env bash

update_umbox() {
    local umbox_name="$1"

    echo "Updating ${umbox_name}"
    cd ${umbox_name}
    time bash ../vm_full_process.sh
    cd ..
    echo "Finished updating ${umbox_name}"
}

echo "Updating all VM umboxes"

for DIR in ./standard/*/   # list directories with full path
do
    DIR=${DIR%*/}          # remove the trailing "/"
    UMBOX_NAME=${DIR##*/}  # remove all path before current directory
    update_umbox ${UMBOX_NAME}
done

echo "Finished updating all VM umboxes"
