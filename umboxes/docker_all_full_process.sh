#!/usr/bin/env bash

update_umbox() {
    local umbox_name="$1"

    echo "Updating ${umbox_name}"
    cd ${umbox_name}
    time bash ../../common/sniffer_docker/build_umbox_image.sh
    cd ..
    echo "Finished updating ${umbox_name}"
}

echo "Updating base umboxes - alerter"
cd common/alerter_docker
bash build_alerter_image.sh
cd ..

echo "Updating base umboxes - sniffer"
cd common/sniffer_docker
bash build_sniffer_image.sh
cd ..

echo "Updating all docker umboxes"

for DIR in ./standard/*/   # list directories with full path
do
    DIR=${DIR%*/}          # remove the trailing "/"
    UMBOX_NAME=${DIR##*/}  # remove all path before current directory
    update_umbox ${UMBOX_NAME}
done

echo "Finished updating all docker umboxes"
