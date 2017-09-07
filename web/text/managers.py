from __future__ import absolute_import, unicode_literals
from collections import OrderedDict

from django.db import models
from django.db.models import Q

class TextManager(models.Manager):

    def get_texts_for(self, number):
        """Get all messages sent by or received by the number."""
        number = number.replace("-", "")

        if not number.isdigit() or len(number) != 7:
            raise ValueError("wrong phone number format: {}".format(number))

        qset = self.filter(Q(sender=number) | Q(recipients__contains=",{},".format(number)))
        return qset.order_by("-date_sent")

    def get_threads_for(self, number):
        """Return the thread messages for the given number.

        This method returns the list of texts sorted by threads.
        Only the most recent text in a thread is displayed.  This
        method will return a dictionary with thread IDs as key, and
        the most recent text of the thread as value.

        """
        threads = OrderedDict()
        for text in self.get_texts_for(number):
            thread = text.thread
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
            q |= Q(sender=number) & Q(recipients=",{},".format(",".join(attempts)))
        q = self.filter(q)
        return q.order_by("-date_sent")
