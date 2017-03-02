"""Module containing the email service.

This service is only used to send emails.  You can call it from anywhere in the game:

```python
from services import email
email.send("from@example.com", "to@example.com", "subject", "body")
```

"""

from email.mime.text import MIMEText
import smtplib
import socket
import re

# Constants
RE_VALID = re.compile(r"[^@]+@[^@]+\.[^@]+")

class EmailService(object):

    """Service to send emails."""

    def __init__(self):
        self.server = None

    def setup(self, hostname="localhost"):
        """Set the email server up."""
        try:
            self.server = smtplib.SMTP(hostname)
        except socket.error:
            self.server = None
            print "The SMTP server couldn't be reached."

    def send(self, origin, recipent, subject, body, error=None):
        """
        Send an email to the specified recipent.

        Args:
            origin: the origin of the message (an email address)
            recipent: the recipent's email address
            subject: the subject of the message (all ASCII)
            body: the body of the message (all ASCII)
            error: the string to log (or display) if an error occurs

        """
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = origin
        msg['To'] = recipent

        # Actually send s the message
        if self.server:
            try:
                self.server.sendmail(origin, [recipent], msg.as_string())
            except smtplib.SMTPException:
                if error:
                    print error
        else:
            if error:
                print error

    def is_email_address(self, email_address):
        """Return true if the specified email address is valid.

        Performs a very basic check on the email address.  The
        only way to know whethter it exists or not it to use it
        (to send an email confirmation).

        This method doesn't need the SMTP server running.

        """
        return RE_VALID.search(email_address) is not None
