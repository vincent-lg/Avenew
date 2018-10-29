# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime

from django.db import models
from django.utils.timezone import make_aware
from evennia.accounts.models import AccountDB
from evennia.utils.idmapper.models import SharedMemoryModel

#from web.mailgun.managers import EmailMessageManager, EmailThreadManager

class EmailAddress(SharedMemoryModel):

    """An email address, optionally linked to an account.."""

    db_display_name = models.CharField(max_length=40, null=True, blank=True, default="")
    db_email = models.CharField(max_length=254, db_index=True, unique=True)
    db_account = models.ForeignKey(AccountDB, null=True, blank=True, on_delete=models.SET_NULL)


class EmailThread(SharedMemoryModel):

    """A thread to group messages."""

    #objects = EmailThreadManager()
    db_subject = models.CharField(max_length=254, default="")
    db_participants = models.ManyToManyField(EmailAddress)
    db_read = models.BooleanField(default=False)


class EmailMessage(SharedMemoryModel):

    """A model representing an email message, part of a thread."""

    #objects = EmailMessageManager()
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
