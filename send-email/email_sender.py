"""
Create and send email messages.

The EmailMessage class constructs SMTP email messages.
The EmailSender class constructs the configuration for an SMTP sever used
to send messages.
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import logging


logging.basicConfig(level=logging.DEBUG)


class EmailMessage:
    """SMTP email message
    """

    def __init__(self, content, subject, sender, receiver, cc=None):
        """Create email message.

        Use `subject`, `content` global variables for subject and message content.
        Use `sender`, `receiver` and `cc` to fill the `From`, `To` and `Cc`
        fields in the email message.
        """

        self.message = MIMEMultipart()
        self.message['From'] = sender
        self.message['To'] = receiver
        self.message['Cc'] = cc
        self.message['Subject'] = subject
        self.message.attach(MIMEText(content, 'plain'))


class EmailSender:
    """SMTP email sender
    """

    def __init__(self, server_name, server_port, server_sender_login, server_sender_password):
        """Create email sender configuration.

        Store SMTP server and login information.
        """

        self.server_name = server_name
        self.server_port = server_port
        self.server_sender_login = server_sender_login
        self.server_sender_password = server_sender_password

    def send(self, email):
        """Send email.

        Create message using the the `create_email()` function.
        Use SMTP API in the `smptlib` package to send message.
        """

        sender = email.message['From']

        # If Cc is present is has to be added to the list of receivers.
        # The `Cc` field was filled by the `create_email()` function.
        toaddrs = [email.message['To']]
        if email.message['Cc']:
            toaddrs.append(email.message['Cc'])
        logging.info("sending message to: " + str(toaddrs))
        context = ssl.create_default_context()
        try:
            # Use TLS/SSL negociation (port 465) or STARTTLS negociation (port 587).
            if self.server_port == 465:
                smtp = smtplib.SMTP_SSL(self.server_name, self.server_port, context=context)
            elif self.server_port == 587:
                smtp = smtplib.SMTP(self.server_name, self.server_port)
                smtp.ehlo()
                smtp.starttls(context=context)
                smtp.ehlo()
            else:
                logging.error("Unknown SMTP port. Not sending email.")
                return
            smtp.login(self.server_sender_login, self.server_sender_password)
            smtp.sendmail(sender, toaddrs, email.message.as_string())
            smtp.quit()
        except Exception as e:
            logging.error("Error sending e-mail: {}".format(e))
