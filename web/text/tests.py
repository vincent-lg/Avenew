# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from web.text.models import *

class TestText(TestCase):

    def setUp(self):
        super(TestText, self).setUp()
        self.n1 = "6917735"
        self.n2 = "6917799"
        self.n3 = "5551234"

    def test_unread(self):
        """Test that the number of unread threads is correctly reported."""
        # Check that all three numbers have 0 unread threads
        self.assertEqual(Text.objects.get_num_unread(self.n1), 0)
        self.assertEqual(Text.objects.get_num_unread(self.n2), 0)
        self.assertEqual(Text.objects.get_num_unread(self.n3), 0)

        # Send one text from n1 to n2
        Text.objects.send(self.n1, [self.n2], "How do?")
        self.assertEqual(Text.objects.get_num_unread(self.n1), 0)
        self.assertEqual(Text.objects.get_num_unread(self.n2), 1)
        self.assertEqual(Text.objects.get_num_unread(self.n3), 0)

        # Send an answer from n2 to n1
        Text.objects.send(self.n2, [self.n1], "Good! You?")
        self.assertEqual(Text.objects.get_num_unread(self.n1), 1)
        self.assertEqual(Text.objects.get_num_unread(self.n2), 0)
        self.assertEqual(Text.objects.get_num_unread(self.n3), 0)

        # Send a text from n3 to n1
        Text.objects.send(self.n3, [self.n1], "Hold!")
        self.assertEqual(Text.objects.get_num_unread(self.n1), 2)
        self.assertEqual(Text.objects.get_num_unread(self.n2), 0)
        self.assertEqual(Text.objects.get_num_unread(self.n3), 0)

    def test_thread(self):
        """Test to send texts and see their threads."""
        # Send one text from n1 to n2
        t1 = Text.objects.send(self.n1, [self.n2], "How do?")
        t2 = Text.objects.send(self.n2, [self.n1], "Good! You?")
        t3 = Text.objects.send(self.n3, [self.n1], "Hold!")
        self.assertEqual(t1.db_thread, t2.db_thread)
        self.assertNotEqual(t1.db_thread, t3.db_thread)
        self.assertNotEqual(t2.db_thread, t3.db_thread)
        self.assertEqual(Thread.objects.all().count(), 2)

    def test_texts_for(self):
        """Check the get_texts_for helper."""
        t1 = Text.objects.send(self.n1, [self.n2], "How do?")
        t2 = Text.objects.send(self.n2, [self.n1], "Good! You?")
        t3 = Text.objects.send(self.n3, [self.n1], "Hold!")
        self.assertIn(t1, Text.objects.get_texts_for(self.n1))
        self.assertIn(t2, Text.objects.get_texts_for(self.n1))
        self.assertIn(t3, Text.objects.get_texts_for(self.n1))
        self.assertIn(t1, Text.objects.get_texts_for(self.n2))
        self.assertIn(t2, Text.objects.get_texts_for(self.n2))
        self.assertNotIn(t3, Text.objects.get_texts_for(self.n2))
        self.assertNotIn(t1, Text.objects.get_texts_for(self.n3))
        self.assertNotIn(t2, Text.objects.get_texts_for(self.n3))
        self.assertIn(t3, Text.objects.get_texts_for(self.n3))

    def test_threads_for(self):
        """Check the get_threads_for helper."""
        t1 = Text.objects.send(self.n1, [self.n2], "How do?")
        t2 = Text.objects.send(self.n2, [self.n1], "Good! You?")
        t3 = Text.objects.send(self.n3, [self.n1], "Hold!")
        self.assertIn(t1.db_thread_id, Text.objects.get_threads_for(self.n1))
        self.assertIn(t3.db_thread_id, Text.objects.get_threads_for(self.n1))
        self.assertIn(t1.db_thread_id, Text.objects.get_threads_for(self.n2))
        self.assertNotIn(t3.db_thread_id, Text.objects.get_threads_for(self.n2))
        self.assertNotIn(t1.db_thread_id, Text.objects.get_threads_for(self.n3))
        self.assertIn(t3.db_thread_id, Text.objects.get_threads_for(self.n3))

    def test_get_texts_with(self):
        """Check the get_texts_with method."""
        t1 = Text.objects.send(self.n1, [self.n2], "How do?")
        t2 = Text.objects.send(self.n2, [self.n1], "Good! You?")
        t3 = Text.objects.send(self.n3, [self.n1], "Hold!")
        self.assertEqual(list(Text.objects.get_texts_with([])), [])
        self.assertEqual(list(Text.objects.get_texts_with([self.n1])), [])
        self.assertEqual(list(Text.objects.get_texts_with([self.n2])), [])
        self.assertIn(t1, Text.objects.get_texts_with([self.n1, self.n2]))
        self.assertIn(t2, Text.objects.get_texts_with([self.n1, self.n2]))
        self.assertNotIn(t3, Text.objects.get_texts_with([self.n1, self.n2]))

        # Try with n3
        self.assertEqual(list(Text.objects.get_texts_with([self.n3])), [])
        self.assertEqual(list(Text.objects.get_texts_with([self.n2, self.n3])), [])
        self.assertNotIn(t1, Text.objects.get_texts_with([self.n1, self.n3]))
        self.assertNotIn(t2, Text.objects.get_texts_with([self.n1, self.n3]))
        self.assertIn(t3, Text.objects.get_texts_with([self.n1, self.n3]))
        self.assertEqual(list(Text.objects.get_texts_with([self.n1, self.n2, self.n3])), [])

    def test_read_unread(self):
        """Test marking a thread as read and unread."""
        t1 = Text.objects.send(self.n1, [self.n2], "How do?")
        self.assertTrue(t1.thread.has_read(self.n1))
        self.assertFalse(t1.thread.has_read(self.n2))

        # Mark the thread has read by n2
        t1.thread.mark_read(self.n2)
        self.assertTrue(t1.thread.has_read(self.n1))
        self.assertTrue(t1.thread.has_read(self.n2))

        # Trying to mark the thread as read by n2 again shouldn't disturb it
        t1.thread.mark_read(self.n2)
        self.assertTrue(t1.thread.has_read(self.n1))
        self.assertTrue(t1.thread.has_read(self.n2))

        # Now, marking the thread as unread by n2
        t1.thread.mark_unread(self.n2)
        self.assertTrue(t1.thread.has_read(self.n1))
        self.assertFalse(t1.thread.has_read(self.n2))

        # Marking the thread as unread by n2 again shouldn't disturb it
        t1.thread.mark_unread(self.n2)
        self.assertTrue(t1.thread.has_read(self.n1))
        self.assertFalse(t1.thread.has_read(self.n2))
