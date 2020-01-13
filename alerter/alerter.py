#!/usr/bin/env python

import os
import json

from filetail import FileTail
import alert_api

# Special alert used to notify that the umbox is ready to work.
UMBOX_READY_ALERT = "umbox-ready"


def send_alerts_from_tail(patterns, file_path, server_ip, id_source):
    """Sends an alert by tailing a file and looking for the given patterns in it."""

    # Send initial alert to indicate that umbox has started properly.
    alert_api.send_umbox_alert(server_ip, alert_text=UMBOX_READY_ALERT, id_source=id_source)

    # Note that this loops continues forever, as tail is constantly blocking and fetching more lines.
    tail = FileTail(file_path, max_wait=3)
    for line in tail:
        for pattern in patterns:
            if pattern['search_text'] in line:
                alert_api.send_umbox_alert(server_ip, alert_text=pattern['alert_text'], alert_details=line)


def load_config():
    """Loads config from external file."""
    with open("config.json") as json_config:
        config = json.load(json_config)
    return config


def main():
    config = load_config()
    full_file_path = os.path.abspath(config["log_file"])
    server_ip = config["control_node_ip"]
    print("Starting log checker on file: " + full_file_path)
    print("Alert handler server set to: " + server_ip)

    send_alerts_from_tail(config["patterns"], full_file_path, server_ip, config["id_source"])


if __name__ == '__main__':
    main()
