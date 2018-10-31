# -*- coding: utf-8 -*-

"""Mailgun utility functions."""


from web.mailgun.models import EmailMessage

send_email = EmailMessage.send
