"""Game services.

A service is just a class devoted to perform certain actions,
like sending emails (the email service).  Services can be
reached and imported here.

"""

from services.email_service import EmailService

email = EmailService()
