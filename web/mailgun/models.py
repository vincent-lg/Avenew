# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import requests
import time

from anymail.message import AnymailMessage
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
NEWS_EMAIL = getattr(settings, "MAILING_LISTS", {}).get("NEWS", "")

class EmailAddress(SharedMemoryModel):

    """An email address, optionally linked to an account.."""

    db_display_name = models.CharField(max_length=40, null=True, blank=True, default="")
    db_email = models.CharField(max_length=254, db_index=True, unique=True)
    db_account = models.ForeignKey(AccountDB, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        if self.db_display_name:
            return self.db_display_name + " <" + self.db_email + ">"
        else:
            return self.db_email

    def subscribe_to_news(self):
        """Add this email address to the news mailing list list."""
        if not API_KEY or not NEWS_EMAIL:
            return

        url = "https://api.mailgun.net/v3/lists/{}/members".format(NEWS_EMAIL)

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


class EmailMessage(SharedMemoryModel):

    """A model representing an email message, part of a thread."""

    objects = EmailManager()
    db_message_id = models.CharField(max_length=254, db_index=True)
    db_sender = models.ForeignKey(EmailAddress)
    db_date_created = models.DateTimeField("date created", editable=False,
            auto_now_add=True, db_index=True)
    db_text = models.TextField()
    db_html = models.TextField()
    db_thread = models.ForeignKey(EmailThread, on_delete=models.CASCADE)

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
