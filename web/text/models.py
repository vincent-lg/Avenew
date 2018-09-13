# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime

from django.db import models
from django.utils.timezone import make_aware
from evennia.utils.idmapper.models import SharedMemoryModel
from evennia.utils.utils import time_format

from web.text.managers import TextManager, ThreadManager

# Global imports
_GAMETIME = None

class Number(SharedMemoryModel):

    """A phone number."""

    db_phone_number = models.CharField(max_length=7, db_index=True)


class Thread(SharedMemoryModel):

    """A thread to group messages."""

    objects = ThreadManager()
    db_name = models.CharField(max_length=30, default="")
    db_recipients = models.ManyToManyField(Number)
    db_read = models.ManyToManyField(Number, related_name='+')


class Text(SharedMemoryModel):

    """A text model, representing a text message."""

    objects = TextManager()
    db_sender = models.ForeignKey(Number)
    db_date_created = models.DateTimeField('date created', editable=False,
            auto_now_add=True, db_index=True)
    db_date_sent = models.DateTimeField('date sent')
    db_content = models.TextField()
    db_thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    db_deleted = models.ManyToManyField(Number, related_name='+')

    def __str__(self):
        return "{}: {}".format(self.id, self.content)

    @property
    def sent_ago(self):
        """Return the human-readable time since sent (X units ago)."""
        global _GAMETIME
        if not _GAMETIME:
            from evennia.utils import gametime as _GAMETIME

        gtime = datetime.datetime.fromtimestamp(_GAMETIME.gametime(absolute=True))
        gtime = make_aware(gtime)

        seconds = (gtime - self.date_sent).total_seconds()
        ago = time_format(seconds, 4)
        return "{} ago".format(ago)

    @property
    def recipients(self):
        """Return the list of recipients, using the thread."""
        recipients = []
        for recipient in self.db_thread.db_recipients.all():
            if recipient != self.sender:
                recipients.append(recipient.db_phone_number)

        return recipients
