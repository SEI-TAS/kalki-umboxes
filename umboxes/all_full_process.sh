#!/usr/bin/env bash

update_umbox() {
    local umbox_name="$1"

    echo "Updating ${umbox_name}"
    cd ${umbox_name}
    time bash ../full_process.sh
    cd ..
    echo "Finished updating ${umbox_name}"
}

echo "Updating all umboxes"
update_umbox "u1-antidos"
update_umbox "u2-http-auth-proxy"
update_umbox "u3-http-auth-proxy-block"
update_umbox "u4-block-all"
update_umbox "u5-sniffer-log-stats"
update_umbox "u6-udoo-brute-force"
update_umbox "u7-udoo-brute-force-block"
update_umbox "u9-phillips-brute-force"
update_umbox "u10-phillips-brute-force-restrict"
echo "Finished updating all umboxes"
