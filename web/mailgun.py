# -*- coding: utf-8 -*-

"""
Web utility functions, specific to Avenew but generic enough to be ported to other projects.

Functions:
    send_email -> send an email using Anymail.
    add_member -> add a member to a mailing list.

"""

from anymail.message import AnymailMessage
from django.conf import settings
from django.utils.html import strip_tags
import requests
import time

from world.log import tasks as log

## Constants
API_KEY = getattr(settings, "ANYMAIL", {}).get("MAILGUN_API_KEY", "The key wasn't specified.")

def send_email(from_email, to, subject, body, html=False):
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

    Returns:
        message_id (None or str): the message ID (Message-Id header) if
        the message was succesfully sent, None otherwise.

    """
    if isinstance(to, str):
        to = [to]

    if html:
        html_body = body
        body = strip_tags(html_body)

    # Create the message
    message = AnymailMessage(subject=subject, body=body, to=to, from_email=from_email)
    if html:
        message.attach_alternative(html_body, "text/html")

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
    return status.message_id if status else None

def add_member(self, list_email, member_name, member_email):
    """
    Add a new member to the specified list.

    Args:
        list_email (str): the list's e-mail address.
        member_name (str): the member name.
        member_email (str): the member email address.

    """
    return requests.post(
        "https://api.mailgun.net/v3/lists/{list_email}/members".format(list_email=list_email),
        auth=('api', API_KEY),
        data={
            'subscribed': True,
            'address': member_email,
            'name': member_name,
        }
    )
