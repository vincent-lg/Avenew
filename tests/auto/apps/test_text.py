# -*- coding: utf-8 -*-

"""
Test for the app text.
"""

from evennia.utils.create import create_object
from evennia.commands.default.tests import CommandTest
from evennia.utils import utils
from mock import Mock

from auto.apps import text as app
from auto.apps import base
from auto.types.high_tech import load_apps
from commands.objects import CmdUse
from web.text.models import Text, Thread

class TestText(CommandTest):

    """Test for the text app."""

    @property
    def screen(self):
        """Get thge current screen for self.user or None."""
        for cmdset in self.user.cmdset.get():
            if cmdset.key == "computer":
                return cmdset.screen

        return None

    @classmethod
    def execute_cmd(cls, caller, command):
        """Execute the command and return the received string."""
        old_msg = caller.msg
        returned_msg = ""
        try:
            caller.msg = Mock()
            caller.execute_cmd(command)
        finally:
            stored_msg = [args[0] if args and args[0] else kwargs.get("text", utils.to_str(kwargs, force_string=True)) \
                          for name, args, kwargs in caller.msg.mock_calls]
            stored_msg = [smsg[0] if isinstance(smsg, tuple) else smsg for smsg in stored_msg]
            returned_msg = "\n".join(str(msg) for msg in stored_msg)
            caller.msg = old_msg

        return returned_msg

    def setUp(self):
        super(TestText, self).setUp()

        # Create a phone in self.char3's inventory
        type(__import__("auto").types.high_tech.PHONE_GENERATOR).script = None
        self.user = create_object("typeclasses.characters.Character", key="user", location=self.room1)
        load_apps()
        self.prototype = create_object("typeclasses.prototypes.PObj", key="aven_phone")
        self.prototype.types.add("phone")
        self.prototype.types.add("computer")
        self.prototype.types.get("computer").apps.add("text")
        self.prototype.types.get("computer").apps.add("contact")

        # Send some default messages already
        self.texts = {
                1: Text.objects.send("6007979", ["5501234"], "Hello there?"),
                2: Text.objects.send("5501234", ["6007979"], "I received that"),
                3: Text.objects.send("5501234", ["2231818"], "Where to?"),
        }
        self.phone1 = self.prototype.create(key="a phone", location=self.user)

    def open(self):
        """Put the smart phone object in use."""
        repr(self.call(CmdUse(), "phone", caller=self.user))

        # Try to get the CmdSet and screen
        self.screen.no_match("text")

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

    def test_main_screen(self):
        """Test that the main screen correctly opoens and display accurate information."""
        self.open()
        self.assertIsInstance(self.screen, app.MainScreen)

        # Check that the text contains some important information
        text = self.screen.get_text()
        self.assertIn("no text", text)
        self.assertIn("|lcnew", text)

        # Try to go back and exit the screen
        self.user.execute_cmd("back")
        self.assertIsInstance(self.screen, base.MainScreen)
        self.user.execute_cmd("exit")
        self.assertIsNone(self.screen)

    def test_new_text(self):
        """Write a new text."""
        self.open()
        self.assertIsInstance(self.screen, app.MainScreen)

        # Try to open a new text
        self.user.execute_cmd("new")
        self.assertIsInstance(self.screen, app.NewTextScreen)
        text = self.screen.get_text()

        # Check that some important are provided in this screen
        self.assertIn("New message", text)
        self.assertIn("|lcsend", text)
        self.assertIn("|lccancel", text)

        # Try to add several valid and invalid phones
        ret = self.execute_cmd(self.user, "to")
        self.assertIn("phone number", ret)
        self.assertIn("add", ret)
        self.assertIn("remove", ret)

        ret = self.execute_cmd(self.user, "to 331")
        self.assertIn("not a valid", ret)

        # Add a valid phone number
        ret = self.execute_cmd(self.user, "to 6007979")
        self.assertIn("added", ret.splitlines()[0])
        self.assertIn("6007979", self.screen.db["recipients"])

        # Add a new one
        ret = self.execute_cmd(self.user, "to 550-1234")
        self.assertIn("added", ret.splitlines()[0])
        self.assertIn("5501234", self.screen.db["recipients"])
        self.assertIn("6007979", self.screen.db["recipients"])

        # Remove the first one
        ret = self.execute_cmd(self.user, "to 600-7979")
        self.assertIn("removed", ret.splitlines()[0])
        self.assertNotIn("6007979", self.screen.db["recipients"])
        self.assertIn("5501234", self.screen.db["recipients"])

        # Enter some text in the app
        self.user.execute_cmd("Hello, this is me!")
        self.assertEqual(self.screen.db["content"], "Hello, this is me!")
        self.user.execute_cmd("And then...")
        self.assertEqual(self.screen.db["content"].splitlines()[1], "And then...")

        # Try to send the text
        ret = self.execute_cmd(self.user, "send")
        self.assertIn("sent successfully", ret)

        # Check that we're back in the ThreadScreen
        self.assertIsInstance(self.screen, app.MainScreen)
        self.assertTrue(len(self.screen.db["threads"]) == 1)

        # Make sure of different error cases
        self.user.execute_cmd("new")
        self.assertIsInstance(self.screen, app.NewTextScreen)
        self.execute_cmd(self.user, "back")
        self.assertIsInstance(self.screen, app.MainScreen)
        self.user.execute_cmd("new")
        self.assertIsInstance(self.screen, app.NewTextScreen)
        self.execute_cmd(self.user, "cancel")
        self.assertIsInstance(self.screen, app.MainScreen)
        self.user.execute_cmd("new")
        self.assertIsInstance(self.screen, app.NewTextScreen)
        ret = self.execute_cmd(self.user, "send")
        self.assertIn("one recipient", ret.splitlines()[0])
        self.assertIsInstance(self.screen, app.NewTextScreen)
        self.user.execute_cmd("to 5501234")
        self.assertIsInstance(self.screen, app.NewTextScreen)
        ret = self.execute_cmd(self.user, "send")
        self.assertIn("empty", ret.splitlines()[0])

    def test_thread(self):
        """Test the thread screen."""
        number = self.phone1.types.get("phone").number
        text = Text.objects.send(number, ["2231818"], "One message")
        thread = text.thread
        self.open()
        self.assertIsInstance(self.screen, app.MainScreen)

        # The screen must contain at least one thread
        self.assertEqual(len(self.screen.db["threads"]), 1)
        text = self.screen.get_text()
        self.assertIn("223-1818", text)

        # Open the one thread
        self.user.execute_cmd("1")
        self.assertIsInstance(self.screen, app.ThreadScreen)
        self.assertEqual(self.screen.db["thread"], thread)

        # Try to write some content
        self.user.execute_cmd("How is it going?")
        self.assertEqual(self.screen.db["content"], "How is it going?")

        # Try to send
        self.user.execute_cmd("send")
        self.assertEqual(list(thread.text_set.all())[-1].content, "How is it going?")
        self.assertIsInstance(self.screen, app.ThreadScreen)

        # Try to go back, just to check
        self.user.execute_cmd("back")
        self.assertIsInstance(self.screen, app.MainScreen)
        self.user.execute_cmd("back")
        self.assertIsInstance(self.screen, base.MainScreen)

    def test_contact(self):
        """Test the contact button on the ThreadScreen."""
        number = self.phone1.types.get("phone").number
        text = Text.objects.send(number, ["2231818"], "One message")
        thread = text.thread
        self.open()
        self.assertIsInstance(self.screen, app.MainScreen)
        self.user.execute_cmd("1")
        self.assertIsInstance(self.screen, app.ThreadScreen)
        self.assertEqual(self.screen.db["thread"], thread)
        self.user.execute_cmd("contact")
        self.assertFalse(isinstance(self.screen, app.ThreadScreen))
        self.user.execute_cmd("back")
        self.assertIsInstance(self.screen, app.ThreadScreen)
        self.user.execute_cmd("back")
        self.assertIsInstance(self.screen, app.MainScreen)
        self.user.execute_cmd("back")
        self.assertIsInstance(self.screen, base.MainScreen)

