#!/usr/bin/env python3
# NOTE: this needs to be run with sudo and python 3. This will only work on Linux due to the use of the AF_SOCKET type.

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

email_server = smtplib.SMTP(host="localhost", port="2555", timeout=3)

msg = MIMEMultipart()
msg['From'] = "kalki@localtest.com"
msg['To'] = "admin1@localtest.com"
msg['Subject'] = "test email"
msg.attach(MIMEText("This is a test", 'plain'))

email_server.send_message(msg)
