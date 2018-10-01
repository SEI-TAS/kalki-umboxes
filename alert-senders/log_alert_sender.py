#!/usr/bin/env python

import time
from filetail import FileTail

import alert_sender

# TODO: make these two configurable.
LOG_PATH = "snort.log"
ALERT_HANDLER_SERVER = u"127.0.0.1"


def forever_file_sender(patterns):
    """Sends an alert if patterns are found in a file. Since they are not removed, once they are found, the alert
    will be send forever, unless the text is externally removed from the file."""

    while True:
        for pattern in patterns:
            if _is_alert_in_file(pattern['search_text'], LOG_PATH):
                alert_sender.send_umbox_alert(ALERT_HANDLER_SERVER, alert_text=pattern['alert_text'])

        time.sleep(1)


def _is_alert_in_file(alert_string, file_path):
    """Checks if an alert for the given string was found in the alert log."""
    alert_found = False

    with open(file_path, "r") as alert_file:
        alert_file_contents = alert_file.read()

        # Check if an alert of the type we want was logged.
        if alert_string in alert_file_contents:
            alert_found = True

    return alert_found


def tail_file_sender(patterns):
    """Sends an alert by tailing a file."""

    tail = FileTail(LOG_PATH, max_wait=3)
    for line in tail:
        for pattern in patterns:
            if pattern['search_text'] in line:
                alert_sender.send_umbox_alert(ALERT_HANDLER_SERVER, alert_text=pattern['alert_text'])


def ping_forever_sender():
    """Sends alerts once a PING message is found, forever."""
    patterns = []
    patterns.append({'search_text': 'ICMP', 'alert_text': 'ping_alert'})

    forever_file_sender(patterns)


def credentials_tail_sender():
    """Sends alerts once credential attacks are found in file, tailing."""
    patterns = []
    patterns.append({'search_text': 'DEFAULT_CRED', 'alert_text': 'login with default credentials'})
    patterns.append({'search_text': 'MULTIPLE_LOGIN', 'alert_text': 'multiple login attempts in 30 min'})

    tail_file_sender(patterns)


def main():
    #ping_forever_sender()
    credentials_tail_sender()


if __name__ == '__main__':
    main()
