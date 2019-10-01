#!/usr/bin/env python

import time

import requests
import netifaces
import ipaddress

ALERT_HANDLER_URL = "/alert/"
ALERT_HANDLER_PORT = 6060


def send_umbox_alert(server_ip, alert_text, alert_details=""):
    """An API request to the Alert Handler to send alerts about the current mbox, using MAC to identify it."""

    # Get the mac of the card we will use for the control plane. Then extract the umbox id.
    local_mac = _local_mac_for_remote_ip(server_ip)
    print("Server IP: " + server_ip + "; local mac: " + str(local_mac))
    if local_mac == "":
        print("Not sending alert. Local MAC not found, server IP not associated to any of the local NICs.")
        return

    umbox_id = int(local_mac[-5:-3], 16) * 100 + int(local_mac[-2:], 16)
    print("Umbox id: " + str(umbox_id))

    # Try sending the alert a couple of times.
    max_retries = 3
    retry_delay = 3
    curr_retry = 0
    print("Sending alert {}".format(alert_text))
    while curr_retry < max_retries:
        try:
            return send_alert(server_ip, alerter_id=umbox_id, alert_text=alert_text, alert_details=alert_details)
        except requests.exceptions.ConnectionError as e:
            curr_retry += 1
            print("Error sending alert: " + str(e))
            if curr_retry < max_retries:
                print("Retrying try {} in {} seconds".format(curr_retry, retry_delay))
                time.sleep(retry_delay)
            else:
                print("Retried too many times, discarding alert.")
                break


def send_alert(server_ip, alerter_id, alert_text, alert_details):
    """A generic API request to Alert Handler."""

    url = "http://" + str(server_ip) + ":" + str(ALERT_HANDLER_PORT) + ALERT_HANDLER_URL
    print(url)
    headers = {}
    headers["Content-Type"] = "application/json"

    payload = {}
    payload['umbox'] = alerter_id
    payload['alert'] = alert_text
    payload['details'] = alert_details

    req = requests.Request('POST', url, headers=headers, json=payload)
    prepared = req.prepare()
    _pretty_print_POST(prepared)

    reply = requests.post(url, json=payload, headers=headers)

    print(reply)
    print(reply.content)
    return reply.content


def _pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in
    this function because it is programmed to be pretty
    printed and may differ from the actual request.
    """
    print('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
        ))


def _local_mac_for_remote_ip(remote_ip):
    """Finds the MAC address of the interface in the same network as the given remote IP address."""
    for interface in netifaces.interfaces():
        addresses = netifaces.ifaddresses(interface)
        try:
            interface_mac = addresses[netifaces.AF_LINK][0]['addr']
            interface_ip_info = addresses[netifaces.AF_INET][0]
            interface_network = ipaddress.ip_network(interface_ip_info['addr'] + "/" + interface_ip_info['netmask'], False)
        except (IndexError, KeyError):
            # Ignore interfaces with missing IP info.
            continue
        if ipaddress.ip_address(remote_ip) in interface_network:
            return interface_mac
    return ""
