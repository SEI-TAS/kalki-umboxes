#!/usr/bin/env python3
# NOTE: this needs to be run with python 3.

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

email_server = smtplib.SMTP(host="10.27.153.3", port="2555", timeout=30)

msg = MIMEMultipart()
msg['From'] = "kalki@localtest.com"
msg['To'] = "admin1@localtest.com"
msg['Subject'] = "test email"
msg.attach(MIMEText("This is a test", 'plain'))

email_server.send_message(msg)
