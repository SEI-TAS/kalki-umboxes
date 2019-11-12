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
