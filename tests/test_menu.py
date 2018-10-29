# -*- coding: utf-8 -*-

"""Test the login menu system."""

from django.conf import settings
from django.core import mail
from evennia.commands.default.tests import CommandTest
from evennia.utils import create

from commands.unloggedin import UnloggedinCmdSet, CmdUnloggedinLook
from typeclasses.accounts import Account

# Force the TEST_SESSION to False
settings.TEST_SESSION = False

class TestMenu(CommandTest):

    """Test the account/character login menu."""

    def setUp(self):
        """Make sure to add the CmdSet to the session."""
        super(TestMenu, self).setUp()
        self.session.cmdset.all()[0].add(CmdUnloggedinLook())
        self.call(CmdUnloggedinLook(), "", caller=self.session)
        self.menutree = self.session.ndb._menutree

        # Force a "test" account to be created
        self.account2 = create.create_account("test", "", "mypassword")
        self.account2.db.valid = True

    @property
    def default_node(self):
        """Return the next, default menu node's name."""
        return self.session.db._menutree.default[0]

    def test_start(self):
        """Test the welcome start."""
        self.assertIsNotNone(self.menutree)
        self.assertIsNotNone(self.menutree.nodetext)

    def test_username(self):
        """Try to connect using an existing username."""
        self.session.execute_cmd("test")
        prompt = self.menutree.nodetext
        self.assertEqual(self.default_node, "password")

    def test_wrong_username(self):
        """Test to login to a non-existent username."""
        self.session.execute_cmd("some other account")
        prompt = self.menutree.nodetext
        self.assertEqual(self.default_node, "username")

    def test_password(self):
        """Test to login to an existing account with correct password."""
        self.session.execute_cmd("test")
        self.session.execute_cmd("mypassword")
        prompt = self.menutree.nodetext
        self.assertEqual(self.default_node, "create_first_name")

    def test_wrong_password(self):
        """Test to login to an existing account with a wrong password."""
        self.session.execute_cmd("test")
        self.session.execute_cmd("notthat")
        self.assertEqual(self.default_node, "password")
        self.assertTrue(self.account2.db._locked)

        # And check that you cannot insist even providing the right password
        self.session.execute_cmd("mypassword")
        prompt = self.menutree.nodetext
        self.assertEqual(self.default_node, "password")

    def test_create_account(self):
        """Try to create an account."""
        # Ask to create a new account
        self.session.execute_cmd("NEW")
        prompt = self.menutree.nodetext
        self.assertEqual(self.default_node, "create_username")

    def test_create_valid_account(self):
        """Try to create an account."""
        self.session.execute_cmd("NEW")

        # Ask to create the account named 'mark'
        self.session.execute_cmd("mark")
        prompt = self.menutree.nodetext
        self.assertEqual(self.default_node, "create_password")

    def test_create_existing_account(self):
        """Try to create an account with an already used name."""
        self.session.execute_cmd("NEW")
        self.session.execute_cmd("test")
        prompt = self.menutree.nodetext
        self.assertIn("already", prompt)
        self.assertEqual(self.default_node, "create_username")

    def test_create_valid_password(self):
        """Test to create a valid password."""
        self.session.execute_cmd("NEW")
        self.session.execute_cmd("mark")
        self.session.execute_cmd("MarksPassword")
        prompt = self.menutree.nodetext
        self.assertEqual(self.default_node, "confirm_password")

    def test_confirm_password(self):
        """Test to create and confirm a valid password."""
        self.session.execute_cmd("NEW")
        self.session.execute_cmd("mark")
        self.session.execute_cmd("MarksPassword")
        self.session.execute_cmd("MarksPassword")
        prompt = self.menutree.nodetext
        self.assertEqual(self.default_node, "email_address")
        account = Account.objects.get(username="mark")
        self.assertTrue(account.check_password("MarksPassword"))

    def test_correct_email(self):
        """Test to send a correct validation emil."""
        self.session.execute_cmd("NEW")
        self.session.execute_cmd("mark")
        self.session.execute_cmd("MarksPassword")
        self.session.execute_cmd("MarksPassword")
        self.session.execute_cmd("test@avenew.net")
        self.assertEqual(self.default_node, "validate_account")
        prompt = self.menutree.nodetext
        account = Account.objects.get(username="mark")
        validation_code = account.db.validation_code
        self.assertTrue(bool(validation_code))

        # Check that the email was correctly sent
        outbox = mail.outbox
        self.assertTrue(bool(outbox))
        email = outbox[0]
        self.assertIn("test@avenew.net", email.to)
        self.assertIn(validation_code, email.body)

    def test_validate_account(self):
        """Test to go until account validation."""
        self.session.execute_cmd("NEW")
        self.session.execute_cmd("mark")
        self.session.execute_cmd("MarksPassword")
        self.session.execute_cmd("MarksPassword")
        self.session.execute_cmd("test@avenew.net")
        account = Account.objects.get(username="mark")
        validation_code = account.db.validation_code
        self.session.execute_cmd(validation_code)
        self.assertEqual(self.default_node, "create_first_name")
        self.assertTrue(account.db.valid)
