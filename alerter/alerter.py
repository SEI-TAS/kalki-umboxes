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
                alert_api.send_umbox_alert(server_ip, alert_text=pattern['alert_text'], alert_details=line, id_source=id_source)


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
