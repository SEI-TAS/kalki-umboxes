# 
#  Kalki - A Software-Defined IoT Security Platform
#  Copyright 2020 Carnegie Mellon University.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
#  [DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.
#  This Software includes and/or makes use of the following Third-Party Software subject to its own license:
#  1. Google Guava (https://github.com/google/guava) Copyright 2007 The Guava Authors.
#  2. JSON.simple (https://code.google.com/archive/p/json-simple/) Copyright 2006-2009 Yidong Fang, Chris Nokleberg.
#  3. JUnit (https://junit.org/junit5/docs/5.0.1/api/overview-summary.html) Copyright 2020 The JUnit Team.
#  4. Play Framework (https://www.playframework.com/) Copyright 2020 Lightbend Inc..
#  5. PostgreSQL (https://opensource.org/licenses/postgresql) Copyright 1996-2020 The PostgreSQL Global Development Group.
#  6. Jackson (https://github.com/FasterXML/jackson-core) Copyright 2013 FasterXML.
#  7. JSON (https://www.json.org/license.html) Copyright 2002 JSON.org.
#  8. Apache Commons (https://commons.apache.org/) Copyright 2004 The Apache Software Foundation.
#  9. RuleBook (https://github.com/deliveredtechnologies/rulebook/blob/develop/LICENSE.txt) Copyright 2020 Delivered Technologies.
#  10. SLF4J (http://www.slf4j.org/license.html) Copyright 2004-2017 QOS.ch.
#  11. Eclipse Jetty (https://www.eclipse.org/jetty/licenses.html) Copyright 1995-2020 Mort Bay Consulting Pty Ltd and others..
#  12. Mockito (https://github.com/mockito/mockito/wiki/License) Copyright 2007 Mockito contributors.
#  13. SubEtha SMTP (https://github.com/voodoodyne/subethasmtp) Copyright 2006-2007 SubEthaMail.org.
#  14. JSch - Java Secure Channel (http://www.jcraft.com/jsch/) Copyright 2002-2015 Atsuhiko Yamanaka, JCraft,Inc. .
#  15. ouimeaux (https://github.com/iancmcc/ouimeaux) Copyright 2014 Ian McCracken.
#  16. Flask (https://github.com/pallets/flask) Copyright 2010 Pallets.
#  17. Flask-RESTful (https://github.com/flask-restful/flask-restful) Copyright 2013 Twilio, Inc..
#  18. libvirt-python (https://github.com/libvirt/libvirt-python) Copyright 2016 RedHat, Fedora project.
#  19. Requests: HTTP for Humans (https://github.com/psf/requests) Copyright 2019 Kenneth Reitz.
#  20. netifaces (https://github.com/al45tair/netifaces) Copyright 2007-2018 Alastair Houghton.
#  21. ipaddress (https://github.com/phihag/ipaddress) Copyright 2001-2014 Python Software Foundation.
#  DM20-0543
#
#
#!/usr/bin/env python

import time
import socket

import requests
import netifaces
import ipaddress

ALERT_HANDLER_URL = "/alert/"
ALERT_HANDLER_PORT = 6060


def send_umbox_alert(server_ip, alert_text, alert_details="", id_source="mac"):
    """An API request to the Alert Handler to send alerts about the current mbox, using MAC to identify it."""

    if id_source == "mac":
        # Gets the umbox ID from the NIC's MAC.
        umbox_id = _get_umbox_id_from_mac(server_ip)
    else:
        umbox_id = _get_umbox_id_from_hostname()

    if umbox_id is None:
        print("Umbox ID not found, can't send alert.")
        return

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


def _get_umbox_id_from_mac(server_ip):
    # Get the mac of the card we will use for the control plane. Then extract the umbox id.
    local_mac = _local_mac_for_remote_ip(server_ip)
    print("Server IP: " + server_ip + "; local mac: " + str(local_mac))
    if local_mac == "":
        print("Local MAC not found, server IP not associated to any of the local NICs.")
        return None

    umbox_id = int(local_mac[-5:-3], 16) * 100 + int(local_mac[-2:], 16)
    print("Umbox id: " + str(umbox_id))
    return umbox_id


def _get_umbox_id_from_hostname():
    hostname = socket.gethostname()
    umbox_id = hostname.replace("umbox-", "")
    print("Umbox id: " + str(umbox_id))
    return umbox_id


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
