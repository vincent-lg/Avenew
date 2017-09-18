# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from evennia.utils.idmapper.models import SharedMemoryModel

from web.text.managers import TextManager

class Thread(SharedMemoryModel):

    """A thread to group messages."""

    db_name = models.CharField(max_length=30, default="")


class Text(SharedMemoryModel):

    """A text model, representing a text message."""

    objects = TextManager()
    db_sender = models.CharField(max_length=7)
    db_recipients = models.TextField()
    db_date_created = models.DateTimeField('date created', editable=False,
            auto_now_add=True, db_index=True)
    db_date_sent = models.DateTimeField('date sent')
    db_content = models.TextField()
    db_thread = models.ForeignKey(Thread, on_delete=models.CASCADE)

    def __str__(self):
        return "{}: {}".format(self.id, self.content)
