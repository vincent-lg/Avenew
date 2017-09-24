"""
Test for the contact app.
"""

from evennia.utils.create import create_object
from evennia.commands.default.tests import CommandTest
from evennia.utils import utils
from mock import Mock

from auto.apps import contact as app
from auto.apps import base
from auto.types.high_tech import load_apps
from commands.objects import CmdUse

class TestContact(CommandTest):

    """Test for the contact app."""

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
        super(TestContact, self).setUp()

        # Create a phone in self.char3's inventory
        type(__import__("auto").types.high_tech.PHONE_GENERATOR).script = None
        self.user = create_object("typeclasses.characters.Character", key="user", location=self.room1)
        load_apps()
        self.prototype = create_object("typeclasses.prototypes.PObj", key="aven_phone")
        self.prototype.types.add("phone")
        self.prototype.types.add("computer")
        self.prototype.types.get("computer").apps.add("text")
        self.prototype.types.get("computer").apps.add("contact")
        self.phone1 = self.prototype.create(key="a phone", location=self.user)

    def open(self):
        """Put the smart phone object in use."""
        self.call(CmdUse(), "phone", caller=self.user)

        # Try to get the CmdSet and screen
        self.screen.no_match("contact")

    def test_main_screen(self):
        """Test that the main screen correctly opoens and display accurate information."""
        self.open()
        self.assertIsInstance(self.screen, app.MainScreen)

        # Check that the text contains some important information
        text = self.screen.get_text()
        self.assertIn("no contact", text)
        self.assertIn("|lcnew", text)

        # Try to go back and exit the screen
        self.execute_cmd(self.user, "back")
        self.assertIsInstance(self.screen, base.MainScreen)
        self.user.execute_cmd("exit")
        self.assertIsNone(self.screen)

    def test_new_contact(self):
        """Test to add a new contact."""
        self.open()
        self.assertIsInstance(self.screen, app.MainScreen)
        self.execute_cmd(self.user, "new")
        self.assertIsInstance(self.screen, app.ContactScreen)

        # Trying to save at this point will cause an error
        text = self.execute_cmd(self.user, "done")
        self.assertIsInstance(self.screen, app.ContactScreen)
        self.assertIn("first name", text)
        self.assertIn("last name", text)

        # Try to set it all up
        self.execute_cmd(self.user, "first Helga",)
        self.assertEqual(self.screen.db["first_name"], "Helga")
        self.execute_cmd(self.user, "last Hufflepuff",)
        self.assertEqual(self.screen.db["last_name"], "Hufflepuff")
        self.execute_cmd(self.user, "number 111-3535",)
        self.assertEqual(self.screen.db["phone_number"], "1113535")
        self.execute_cmd(self.user, "done")
        self.assertIsInstance(self.screen, app.MainScreen)

        # Check that the new contact was created
        self.assertEqual(self.screen.app.format("111-3535",), "Helga Hufflepuff")

        # Try to open a contact and back
        self.execute_cmd(self.user, "1")
        self.assertIsInstance(self.screen, app.ContactScreen)
        self.execute_cmd(self.user, "back")
        self.assertIsInstance(self.screen, app.MainScreen)
        self.execute_cmd(self.user, "back")
        self.assertIsInstance(self.screen, base.MainScreen)
