# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from evennia_wiki.models import Page, Revision

class TestPages(TestCase):

    def test_hierarchy(self):
        """Test the hierarchy of wiki pages."""
        root = Page.objects.create(address="")
        self.assertEqual(root.address, "")
