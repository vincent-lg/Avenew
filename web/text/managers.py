from __future__ import absolute_import, unicode_literals
import datetime
from collections import OrderedDict

from django.db import models
from django.db.models import Q, Count
from django.utils.timezone import make_aware

# Global imports
_GAMETIME = None
_THREAD = None
_NUMBER = None

class ThreadManager(models.Manager):

    """Thread manager."""

    def get_thread(self, numbers):
        numbers = [number.replace("-", "") for number in numbers]
        query = self.annotate(num_recipients=Count("db_recipients"))
        for number in numbers:
            query = query.filter(db_recipients__db_phone_number=number)
        query = query.filter(num_recipients=len(numbers))
        return query.first() if query.count() else None

class TextManager(models.Manager):

    def get_texts_for(self, number):
        """Get all messages sent by or received by the number."""
        number = number.replace("-", "")

        if not number.isdigit() or len(number) != 7:
            raise ValueError("wrong phone number format: {}".format(number))

        q = self.filter(db_thread__db_recipients__db_phone_number=number)
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
        """Return the list of texts of these numbers.

        Args:
            numbers (list of str): the phone numbers to query.

        """
        numbers = [number.replace("-", "") for number in numbers]
        query = self.annotate(num_recipients=Count("db_thread__db_recipients"))
        for number in numbers:
            query = query.filter(db_thread__db_recipients__db_phone_number=number)
        query = query.filter(num_recipients=len(numbers))
        return query.order_by("-db_date_sent")

    def get_num_unread(self, number):
        """Get the number of unread threads for number.

        Args:
            number (str): the number in question.

        """
        global _THREAD
        if not _THREAD:
            from web.text.models import Thread as _THREAD

        number = number.replace("-", "")
        q = _THREAD.objects.filter(db_recipients__db_phone_number=number)
        q = q.exclude(db_read__db_phone_number=number)
        return q.count()

    def send(self, sender, recipients, content):
        """Send a text message from `number` to `recipients`.

        Args:
            sender (str): the number (7-digit).
            recipients (list of str): a list of 7-digit strings.
            content (str): the text of the message.

        Returns:
            text (Text): the newly-sent text message.

        """
        global _GAMETIME, _THREAD, _NUMBER
        if not _GAMETIME:
            from evennia.utils import gametime as _GAMETIME
        if not _THREAD:
            from web.text.models import Thread as _THREAD
        if not _NUMBER:
            from web.text.models import Number as _NUMBER

        # First, get the sender's phone number
        recipients = [sender] + recipients
        try:
            sender = _NUMBER.objects.get(db_phone_number=sender)
        except _NUMBER.DoesNotExist:
            sender = _NUMBER(db_phone_number=sender)
            sender.save()

        gtime = datetime.datetime.fromtimestamp(_GAMETIME.gametime(absolute=True))
        gtime = make_aware(gtime)

        # Look for a thread or create one
        thread = _THREAD.objects.get_thread(recipients)
        if thread is None:
            thread = _THREAD()
            thread.save()

            # For every participant, add it as recipient
            for number in recipients:
                try:
                    recipient = _NUMBER.objects.get(db_phone_number=number)
                except _NUMBER.DoesNotExist:
                    recipient = _NUMBER(db_phone_number=number)
                    recipient.save()
                thread.db_recipients.add(recipient)

        thread.db_read.clear()
        thread.db_read.add(sender)
        return thread.text_set.create(
                db_sender=sender, db_content=content, db_date_sent=gtime)
