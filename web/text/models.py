# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from web.text.managers import TextManager

class Thread(models.Model):

    """A thread to group messages."""

    name = models.CharField(max_length=30, default="")


class Text(models.Model):

    """A text model, representing a text message."""

    objects = TextManager()
    sender = models.CharField(max_length=7)
    recipients = models.TextField()
    date_sent = models.DateTimeField('date sent', auto_now_add=True)
    content = models.TextField()
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)

    def __str__(self):
        return "{}: {}".format(self.id, self.content)
