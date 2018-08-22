import time

import requests
import webutils

# TODO: make these two configurable.
LOG_PATH = "snort.log"
ALERT_HANDLER_SERVER = u"192.168.122.41"

ALERT_HANDLER_URL = "/alert/"
ALERT_HANDLER_PORT = 6060


def is_alert_in_file(alert_string, file_path):
    """Checks if an alert for the given string was found in the alert log."""
    alert_found = False

    with open(file_path, "r") as alert_file:
        alert_file_contents = alert_file.read()

        # Check if an alert of the type we want was logged.
        if alert_string in alert_file_contents:
            alert_found = True

    return alert_found


def send_request_to_handler(umbox_id, alert_text):
    """A generic API request to Alert Handler."""

    url = "http://" + str(ALERT_HANDLER_SERVER) + ":" + str(ALERT_HANDLER_PORT) + ALERT_HANDLER_URL
    print url
    headers = {}
    headers["Content-Type"] = "application/json"

    payload = {}
    payload['umbox'] = umbox_id
    payload['alert'] = alert_text

    req = requests.Request('POST', url, headers=headers, json=payload)
    prepared = req.prepare()
    webutils.pretty_print_POST(prepared)

    reply = requests.post(url, json=payload, headers=headers)

    print reply
    print reply.content
    return reply.content


def main():

    # Get the mac of the card we will use for the control plane. It will be used as the ID for this umbox.
    LOCAL_MAC = webutils.local_mac_for_remote_ip(ALERT_HANDLER_SERVER)

    # All patterns we want to find in the log file.
    patterns = []
    patterns.append({'search_text': 'ICMP', 'alert_text': 'ping_alert'})

    while True:
        for pattern in patterns:
            if is_alert_in_file(pattern['search_text'], LOG_PATH):
                send_request_to_handler(umbox_id=LOCAL_MAC, alert_text=pattern['alert_text'])

        time.sleep(1)


if __name__ == '__main__':
    main()
