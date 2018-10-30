# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class MailgunConfig(AppConfig):
    name = 'web.mailgun'

    def ready(self):
        from . import signals
