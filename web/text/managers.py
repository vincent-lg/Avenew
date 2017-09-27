from __future__ import absolute_import, unicode_literals
import datetime
from collections import OrderedDict

from django.db import models
from django.db.models import Q
from django.utils.timezone import make_aware

# Global imports
_GAMETIME = None
_THREAD = None

class TextManager(models.Manager):

    def get_texts_for(self, number):
        """Get all messages sent by or received by the number."""
        number = number.replace("-", "")

        if not number.isdigit() or len(number) != 7:
            raise ValueError("wrong phone number format: {}".format(number))

        q = self.filter(Q(db_sender=number) | Q(db_recipients__contains=",{},".format(number)))
        return q.order_by("-db_date_sent")

    def get_threads_for(self, number):
        """Return the thread messages for the given number.

        This method returns the list of texts sorted by threads.
        Only the most recent text in a thread is displayed.  This
        method will return a dictionary with thread IDs as key, and
        the most recent text of the thread as value.

        """
        threads = OrderedDict()
        for text in self.get_texts_for(number):
            thread = text.db_thread
            if thread and thread.id not in threads:
                threads[thread.id] = text

        return threads

    def get_texts_with(self, numbers):
        """Return the text messages sent/received by numbers."""
        q = Q()
        for number in numbers:
            attempts = list(numbers)
            attempts.remove(number)
            attempts.sort()
            q |= Q(db_sender=number) & Q(db_recipients=",{},".format(",".join(attempts)))
        q = self.filter(q)
        return q.order_by("-db_date_sent")

    def get_nb_unread(self, number):
        """Get the number of unread threads for number.

        Args:
            number (str): the number in question.

        """
        number = number.replace("-", "")
        q = self.get_texts_for(number)
        q = q.exclude(db_thread__db_read__contains=",{},".format(number))
        nb = 0
        threads = []
        for text in q:
            if text.thread not in threads:
                threads.append(text.thread)
                nb += 1

        print q.query
        return nb

    def send(self, sender, recipients, content):
        """Send a text message from `number` to `recipients`.

        Args:
            sender (str): the number (7-digit).
            recipients (list of str): a list of 7-digit strings.
            content (str): the text of the message.

        Returns:
            text (Text): the newly-sent text message.

        """
        global _GAMETIME, _THREAD
        if not _GAMETIME:
            from evennia.utils import gametime as _GAMETIME
        if not _THREAD:
            from web.text.models import Thread as _THREAD

        gtime = datetime.datetime.fromtimestamp(_GAMETIME.gametime(absolute=True))
        gtime = make_aware(gtime)

        # Look for a thread or create one
        texts = self.get_texts_with([sender] + recipients)
        if texts:
            thread = texts[0].thread
        else:
            thread = _THREAD()
            thread.save()

        recipients = ",{},".format(",".join(sorted(recipients)))
        return thread.text_set.create(
                db_sender=sender, db_recipients=recipients, db_content=content, db_date_sent=gtime)
