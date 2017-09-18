"""
Test for the app text.
"""

from evennia.utils.create import create_object
from evennia.utils.test_resources import EvenniaTest

from web.text.models import Text, Thread

class TestText(EvenniaTest):

    """Test for the text app."""

    def setUp(self):
        super(TestText, self).setUp()

        # Send some default messages already
        self.texts = {
                1: Text.objects.send("6007979", ["5501234"], "Hello there?"),
                2: Text.objects.send("5501234", ["6007979"], "I received that"),
                3: Text.objects.send("5501234", ["2231818"], "Where to?"),
        }

    def test_send(self):
        """Test that the send option works correctly and threads are created."""
        # Since text 1 and 2 have same sender/recipients, they should share the same thread
        self.assertEqual(self.texts[1].thread.id, self.texts[2].thread.id)

        # However, 1 and 3 shouldn't share the thread
        self.assertNotEqual(self.texts[1].thread.id, self.texts[3].thread.id)

        # Test to ask different texts set
        # sender 1
        for1 = Text.objects.get_texts_for("6007979")
        self.assertIn(self.texts[1], for1)
        self.assertIn(self.texts[2], for1)
        self.assertNotIn(self.texts[3], for1)

        # sender 2
        for2 = Text.objects.get_texts_for("5501234")
        self.assertIn(self.texts[1], for2)
        self.assertIn(self.texts[2], for2)
        self.assertIn(self.texts[3], for2)

        # sender 3
        for3 = Text.objects.get_texts_for("2231818")
        self.assertNotIn(self.texts[1], for3)
        self.assertNotIn(self.texts[2], for3)
        self.assertIn(self.texts[3], for3)
