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
import sys
import socket
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailServer:
    def __init__(self, config):
        self.config = config

        # Get the basic email attributes
        email_server_address = config["email_server_address"]
        email_server_port = config["email_server_port"]
        self.email_source_address = config["email_source_address"]
        self.destination_address_list = config["email_destination_address_list"]

        # Check to see if the server needs to be logged into
        if config["email_server_login"] == "on":
            # Get the username/password for logging in, and execute log in process
            email_username = config["email_account_username"]
            email_password = config["email_account_password"]
            self.email_server = self.setup_email_login(email_server_address, email_server_port, email_username, email_password)
        else:
            # Set up email server without logging in
            self.email_server = self.setup_email_no_login(email_server_address, email_server_port)

    def setup_email_login(self, host, port, username, password):
        # Try to connect 3 times
        retry_count = 3
        while retry_count > 0:
            try:
                # Establish Connection
                email_server = smtplib.SMTP(host=host, port=port, timeout=30)

                # Start TLS
                email_server.starttls()
                email_server.login(username, password)

                # Successful connection; return the server object
                print("Email reporting set up successfully.", flush=True)
                return email_server
            except:
                print("Failed to connect to " + host + ":" + port + "; Exception: " + sys.exc_info()[0] + "; trying again", flush=True)
                retry_count = retry_count - 1

        print("Failed to connect to " + host + ":" + port + ".  Email unavailable.", flush=True)
        return None

    def setup_email_no_login(self, host, port):
        # Try to connect 3 times
        retry_count = 3
        while retry_count > 0:
            try:
                # Establish Connection
                email_server = smtplib.SMTP(host=host, port=port, timeout=30)

                # Successful connection; return the server object
                print ("Email reporting set up successfully.", flush=True)
                return email_server
            except socket.timeout:
                print("Failed to connect to " + host + ":" + port + ", trying again", flush=True)
                retry_count = retry_count - 1

        print("Failed to connect to " + host + ":" + port + ".  Email unavailable.", flush=True)
        return None

    def send_emails(self, email_subject, email_body):
        for destination_address in self.destination_address_list:
            self.send_email(destination_address, email_subject, email_body)

    def send_email(self, destination_address, email_subject, email_body):
        # Make sure the email server is connected
        if self.email_server is None:
            print("No valid email server connection.  Email not sent.", flush=True)
            return

            # Email server connection confirmed; Create the message to send
        msg = MIMEMultipart()
        msg['From'] = self.email_source_address
        msg['To'] = destination_address
        msg['Subject'] = email_subject
        msg.attach(MIMEText(email_body, 'plain'))

        # Send the message via the provided server
        try:
            self.email_server.send_message(msg)
        except smtplib.SMTPException:
            print("Failed to send email to " + destination_address, flush=True)

        # Clean up the message
        del msg
