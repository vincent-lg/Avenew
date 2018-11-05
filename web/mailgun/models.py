# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import requests
import time

from anymail.message import AnymailMessage
from anymail.utils import parse_single_address
from django.conf import settings
from django.db import models
from django.utils.html import strip_tags
from django.utils.timezone import make_aware
from evennia.accounts.models import AccountDB
from evennia.utils.idmapper.models import SharedMemoryModel

from web.mailgun.managers import EmailManager
from world.log import tasks as log

## Constants
API_KEY = getattr(settings, "ANYMAIL", {}).get("MAILGUN_API_KEY", "")
OUTGOING_ALIASES = getattr(settings, "OUTGOING_ALIASES", {})

class EmailAddress(SharedMemoryModel):

    """An email address, optionally linked to an account.."""

    db_display_name = models.CharField(max_length=40, null=True, blank=True, default="")
    db_email = models.CharField(max_length=254, db_index=True, unique=True)
    db_account = models.OneToOneField(AccountDB, null=True, blank=True, on_delete=models.SET_NULL, related_name="email_address")

    def __str__(self):
        if self.db_display_name:
            return self.db_display_name + " <" + self.db_email + ">"
        else:
            return self.db_email

    def subscribe_to_news(self):
        """Add this email address to the news mailing list list."""
        news = OUTGOING_ALIASES.get("NEWS", "")
        if not API_KEY or not news:
            return

        url = "https://api.mailgun.net/v3/lists/{}/members".format(news)

        before = time.time()
        res = requests.post(url,
            auth=('api', API_KEY),
            data={
                'subscribed': True,
                'address': self.db_email,
                'name': self.db_display_name,
            }
        )
        after = time.time()
        log.debug("{}s: calling the API at {}".format(round(after - before, 3), url))
        return res


class EmailThread(SharedMemoryModel):

    """A thread to group messages."""

    db_subject = models.CharField(max_length=254, default="")
    db_participants = models.ManyToManyField(EmailAddress)
    db_read = models.BooleanField(default=False)

    def __str__(self):
        count = self.db_participants.count()
        return "{!r} ({} participants)".format(self.db_subject, count)

    @property
    def emails(self):
        """Return the list of emails in this thread, sorted by date."""
        return self.email_messages.order_by("db_date_created")


class EmailMessage(SharedMemoryModel):

    """A model representing an email message, part of a thread."""

    objects = EmailManager()
    db_message_id = models.CharField(max_length=254, db_index=True)
    db_sender = models.ForeignKey(EmailAddress)
    db_date_created = models.DateTimeField("date created", editable=False,
            auto_now_add=True, db_index=True)
    db_text = models.TextField()
    db_html = models.TextField()
    db_thread = models.ForeignKey(EmailThread, on_delete=models.CASCADE, related_name="email_messages")

    def __str__(self):
        return "{} to {}: {!r}".format(self.db_sender, ", ".join([str(addr) for addr in self.to]), self.db_thread.db_subject)

    @property
    def to(self):
        """Return the list of email addresses, using the thread.

        The sender is ignored from this list.

        """
        to = []
        for address in self.db_thread.db_participants.all():
            if address != self.sender:
                to.append(address)

        return to

    @classmethod
    def send(cls, from_email, to, subject, body, html=False,
            in_reply_to=None, store=True):
        """
        Send the email, returning None or the message ID.

        Args:
            from_email (str): the address ffrom which this message is coming.
            to (str or list of str): the recipient's address(es).
            subject (str): the email subject.
            body (str): the content of the email (see the keyword arguments).

        Kwargs:
            html (bool, optional): if set to True, the specified body is
                    treated as HTML.  The raw (stripped but NOT sanitized) body
                    is sent as plain text.
            in_reply_to (str, optional): the previous message ID in the thread.
            store (bool, optional): store the message in the database (True by default).

        Returns:
            message_id (None or str): the message ID (Message-Id header) if
            the message was succesfully sent, None otherwise.

        """
        if "@" not in from_email:
            # We assume this is an alias
            if from_email not in OUTGOING_ALIASES:
                log.warning("The {!r} alias wasn't set in the 'OUTGOING_ALIASES' setting, aborting.".format(from_email))
                return

            from_email = OUTGOING_ALIASES.get(from_email)

        if isinstance(to, basestring):
            to = [to]

        if html:
            html_body = body
            body = strip_tags(html_body)

        # Create the message
        message = AnymailMessage(subject=subject, body=body, to=to, from_email=from_email)
        if html:
            message.attach_alternative(html_body, "text/html")

        if in_reply_to:
            message.extra_headers["In-Reply-To"] = in_reply_to

        # Send the message (this might block everything for a couple of seconds)
        before = time.time()
        message.send()
        after = time.time()

        # Check the status, returning the message_id if possible
        status = message.anymail_status
        results = status.status if status and status.status else {"unknownable"}
        method = log.info if status and status.message_id else log.warning
        method("{time}s: an email was sent from {origin} to {to}: {status}".format(
                time=round(after - before, 3), origin=from_email,
                to=", ".join([addr for addr in to]),
                status=", ".join([msg for msg in results])))
        message_id = status.message_id if status else None

        # If store is True, create the appropriate message
        if store:
            text = body
            html = html_body if html else ""

            # Convert from_email
            from_email = parse_single_address(from_email)
            from_email, _ = EmailAddress.objects.get_or_create(db_email=from_email.addr_spec,
                    defaults={"db_display_name": from_email.display_name})

            # Find the to and convert to EmailAddresses
            to = [parse_single_address(addr) for addr in to]
            for i, address in enumerate(to):
                to[i], _ = EmailAddress.objects.get_or_create(db_email=address.addr_spec,
                    defaults={"db_display_name": address.display_name})

            # If there's an in_reply_to, don't create a new thread
            if in_reply_to:
                try:
                    in_reply_msg = EmailMessage.objects.get(db_message_id=in_reply_to)
                except EmailMessage.DoesNotExist:
                    raise ValueError("the specified in_reply_to doesn't match any existing email: {!r}".format(in_reply_to))

                thread = in_reply_msg.db_thread
            else:
                thread = EmailThread(db_subject=subject)
                thread.save()

            for email in [from_email] + to:
                thread.db_participants.add(email)

            # Create the EmailMessage
            email = EmailMessage(db_thread=thread, db_sender=from_email, db_message_id=message_id, db_text=text, db_html=html)
            email.save()

        return message_id
