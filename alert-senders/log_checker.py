#!/usr/bin/env python

import time
import os
from argparse import ArgumentParser

from filetail import FileTail
import alerts


def send_alerts_from_file(patterns, file_path, server_ip):
    """Sends an alert if patterns are found in a file. Since they are not removed, once they are found, the alert
    will be send forever, unless the text is externally removed from the file."""

    while True:
        for pattern in patterns:
            if _is_string_in_file(pattern['search_text'], file_path):
                alerts.send_umbox_alert(server_ip, alert_text=pattern['alert_text'])

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


def send_alerts_from_tail(patterns, file_path, server_ip):
    """Sends an alert by tailing a file and looking for the given patterns in it."""

    tail = FileTail(file_path, max_wait=3)
    for line in tail:
        for pattern in patterns:
            if pattern['search_text'] in line:
                alerts.send_umbox_alert(server_ip, alert_text=pattern['alert_text'])


def send_ping_alerts_from_file(file_path, server_ip):
    """Sends alerts once a PING message is found, forever."""
    patterns = []
    patterns.append({'search_text': 'ICMP', 'alert_text': 'ping_alert'})

    send_alerts_from_file(patterns, file_path, server_ip)


def send_credential_alerts_from_tail(file_path, server_ip):
    """Sends alerts once credential attacks are found in file, tailing."""
    patterns = []
    patterns.append({'search_text': 'DEFAULT_CRED', 'alert_text': 'default-login'})
    patterns.append({'search_text': 'MULTIPLE_LOGIN', 'alert_text': 'max-login-attempts'})

    send_alerts_from_tail(patterns, file_path, server_ip)


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest="logfile", default=True, help="log file to check")
    parser.add_argument("-s", "--server", dest="server", default=True, help="alert handler server IP")
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    full_file_path = os.path.abspath(args.logfile)
    server_ip = args.server
    print("Starting log checker on file: " + full_file_path)
    print("Alert handler server set to: " + server_ip)
    #send_ping_alerts_from_file(full_file_path, server_ip)
    send_credential_alerts_from_tail(full_file_path, server_ip)


if __name__ == '__main__':
    main()
