#!/usr/bin/env python

import time
from filetail import FileTail

import alerts

# TODO: make these two configurable.
LOG_PATH = "sniffer.log"
ALERT_HANDLER_SERVER = u"127.0.0.1"


def send_alerts_from_file(patterns, file_path):
    """Sends an alert if patterns are found in a file. Since they are not removed, once they are found, the alert
    will be send forever, unless the text is externally removed from the file."""

    while True:
        for pattern in patterns:
            if _is_string_in_file(pattern['search_text'], file_path):
                alerts.send_umbox_alert(ALERT_HANDLER_SERVER, alert_text=pattern['alert_text'])

        time.sleep(1)


def _is_string_in_file(search_string, file_path):
    """Checks if a given string was found in the alert log."""
    string_found = False

    with open(file_path, "r") as file_to_check:
        file_contents = file_to_check.read()

        # Check if we can find the string logged.
        if search_string in file_contents:
            string_found = True

    return string_found


def send_alerts_from_tail(patterns, file_path):
    """Sends an alert by tailing a file and looking for the given patterns in it."""

    tail = FileTail(file_path, max_wait=3)
    for line in tail:
        for pattern in patterns:
            if pattern['search_text'] in line:
                alerts.send_umbox_alert(ALERT_HANDLER_SERVER, alert_text=pattern['alert_text'])


def send_ping_alerts_from_file():
    """Sends alerts once a PING message is found, forever."""
    patterns = []
    patterns.append({'search_text': 'ICMP', 'alert_text': 'ping_alert'})

    send_alerts_from_file(patterns, LOG_PATH)


def send_credential_alerts_from_tail():
    """Sends alerts once credential attacks are found in file, tailing."""
    patterns = []
    patterns.append({'search_text': 'DEFAULT_CRED', 'alert_text': 'login with default credentials'})
    patterns.append({'search_text': 'MULTIPLE_LOGIN', 'alert_text': 'multiple login attempts in 30 min'})

    send_alerts_from_tail(patterns, LOG_PATH)


def main():
    #send_ping_alerts_from_file()
    send_credential_alerts_from_tail()


if __name__ == '__main__':
    main()
