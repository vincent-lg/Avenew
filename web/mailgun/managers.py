from __future__ import absolute_import, unicode_literals

from django.db import models
from django.db.models import Q, Count
from anymail.inbound import AnymailInboundMessage


class EmailManager(models.Manager):

    """Email manager, to create emails."""

    @classmethod
    def create_from_anymail(self, message):
        """
        Create from an anymail.inbound.AnymailInboundMessage.

        If you have a raw text or email.Message object, you could use the
        `anymail.inbound.AnymailInboundMessage` class functions to build
        something to pass this method.

        """
        from .models import *
        # Find the from and convert to an EmailAddress
        from_email = message.from_email
        from_email, _ = EmailAddress.objects.get_or_create(db_email=from_email.addr_spec,
                defaults={"db_display_name": from_email.display_name})
        from_email.save()
        # Find the to and convert to EmailAddresses
        to = message.to
        for i, address in enumerate(to):
            to[i], _ = EmailAddress.objects.get_or_create(db_email=address.addr_spec,
                defaults={"db_display_name": address.display_name})
            to[i].save()

        # Extract the subject, date, message_id, text and HTML
        subject = message.subject if message.subject else ""
        date = message.date
        message_id = message["Message-ID"]
        text = message.text if message.text else ""
        html = message.html if message.html else ""

        # Connect to an existing thread, if there's an in-reply-to
        thread = None
        if "in-reply-to" in message:
            in_reply_to = message["in-reply-to"]

            try:
                in_reply_msg = EmailMessage.objects.get(db_message_id=in_reply_to)
            except EmailMessage.DoesNotExist:
                pass
            else:
                thread = in_reply_msg.db_thread

        if thread is None:
            thread = EmailThread(db_subject=subject)
            # Add all the participants
            thread.save()
            for email in [from_email] + to:
                thread.db_participants.add(email)

        # Create the EmailMessage
        email = EmailMessage(db_thread=thread, db_date_created=date, db_sender=from_email, db_message_id=message_id, db_text=text, db_html=html)
        email.save()
        return email
