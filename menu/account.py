# -*- coding: utf-8 -*-

"""This module contains the account connexion/creation menu nodes.

start: First login, prompted for username
    'new': create_account
    (any): username
username: check that the username exists
    'b': pre_start
    (any): password (if exists) or username (if not)

"""

from hashlib import sha256
from random import choice
import re
from smtplib import SMTPException
import socket
from textwrap import dedent

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from evennia import logger
from evennia.server.models import ServerConfig
from evennia.utils import create, evmenu
from evennia.utils.utils import delay, random_string_from_module

from menu.character import _login, _options_choose_characters, _text_choose_characters
from typeclasses.accounts import Account
from web.mailgun.utils import send_email

## Constants
CONNECTION_SCREEN_MODULE = settings.CONNECTION_SCREEN_MODULE
LEN_PASSWD = 6
RE_VALID_USERNAME = re.compile(r"^[a-z0-9_.]{3,}$", re.I)

## Connection nodes
def start(caller):
    """The user should enter his/her username or NEW to create one.

    This node is called at the very beginning of the menu, when
    a session has been created OR if an error occurs further
    down the menu tree.  From there, users can either enter a
    username (if this username exists) or type NEW (capitalized
    or not) to create a new account.

    """
    text = random_string_from_module(CONNECTION_SCREEN_MODULE)
    text += "\n\nEnter your username or |wNEW|n to create an account."
    options = (
        {
            "key": "new",
            "desc": "Create a new character.",
            "goto": "create_account",
        },
        {
            "key": "_default",
            "desc": "Login to an existing account.",
            "goto": "username",
        },
    )
    return text, options

def username(caller, input):
    """Check that the username is an existing account.

    Check that the specified username exists.  If the username doesn't
    exist, display an error message and ask the user to either
    enter 'b' to go back, or to try again.
    If it does exist, move to the next node (enter password).

    """
    input = input.strip()
    accounts = Account.objects.filter(username__iexact=input)
    account = accounts[0] if accounts else None
    if account is None:
        text = dedent("""
            |rThe username {} doesn't exist yet.  Have you created it?|n
                Type |wb|n to go back to the login screen.
                Or try another name.
        """.strip("\n")).format(input)
        options = (
            {
                "key": "b",
                "desc": "Go back to the login screen.",
                "goto": "pre_start",
            },
            {
                "key": "_default",
                "desc": "Try again.",
                "goto": "username",
            },
        )
    else:
        caller.db._account = account
        locked = account.db._locked

        # The account is temporarily locked when a wrong password
        # has been supplied.  This lock shouldn't last more than
        # 3 seconds.
        if locked:
            text = "Please wait..."
        else:
            text = "Enter the password for the account {}.".format(
                    account.name)

        # Disables echo for the password
        caller.msg(echo=False)
        options = (
            {
                "key": "_default",
                "desc": "Enter your account's password.",
                "goto": "password",
            },
        )

    return text, options

def password(caller, input):
    """Ask the user to enter the password to this account.

    This is assuming the user exists (see 'create_username' and
    'create_password').  This node "loops" if needed:  if the
    user specifies a wrong password, offers the user to try
    again or to go back by entering 'b'.
    If the password is correct, then login.

    """
    input = input.strip()
    text = ""
    options = (
        {
            "key": "_default",
            "desc": "Enter your password.",
            "goto": "password",
        },
    )

    # Check the password
    account = caller.db._account

    # If the account is locked, the user has to wait (maximum
    # 3 seconds) before retrying
    if account.db._locked:
        text = "|gPlease wait, you cannot enter your password yet.|n"
        return text, options

    bans = ServerConfig.objects.conf("server_bans")
    banned = bans and (any(tup[0] == account.name.lower() for tup in bans) \
            or any(tup[2].match(caller.address) for tup in bans if tup[2]))

    if not account.check_password(input):
        text = dedent("""
            |rIncorrect password.|n
                Type |wb|n to go back to the login screen.
                Or wait 3 seconds before trying a new password.
        """.strip("\n"))

        # Loops on the same node, lock for 3 seconds
        account.db._locked = True
        delay(3, _wrong_password, account)
        options = (
            {
                "key": "b",
                "desc": "Go back to the login screen.",
                "goto": "pre_start",
            },
            {
                "key": "_default",
                "desc": "Enter your password again.",
                "goto": "password",
            },
        )
    elif banned:
        # This is a banned IP or name
        string = dedent("""
            |rYou have been banned and cannot continue from here.|n
            If you feel this ban is in error, please email an admin.
        """.strip("\n"))
        caller.msg(string)
        caller.sessionhandler.disconnect(
                caller, "Good bye!  Disconnecting...")
    else:
        # The password is correct, we can log into the account.
        caller.msg(echo=True)
        if not account.email:
            # Redirects to the node to set an email address
            text = _text_email_address(account)
            options = (
                {
                    "key": "_default",
                    "desc": "Enter your email address.",
                    "goto": "email_address",
                },
            )
        elif not account.db.valid:
            # Redirects to the node for the validation code
            text = "Enter your 4-digit validation code."
            options = (
                {
                    "key": "_default",
                    "desc": "Enter your validation code.",
                    "goto": "validate_account",
                },
            )
        else:
            _login(caller, account)
            text = ""
            options = _options_choose_characters(account)
            if not account.db._playable_characters:
                options = (
                    {
                        "key": "_default",
                        "desc": "Enter your new character's first name.",
                        "goto": "create_first_name",
                    },
                )

    return text, options

# New account/account nodes
def create_account(caller):
    """Create a new account.

    This node simply prompts the user to enter a username.
    The input is redirected to 'create_username'.

    """
    text = dedent("""
        Welcome to Avenew!  We're glad you decided to create an account here.
        You should begin by providing a username for this account.  It will
        be asked of you each time you log in.  Account names can be anything,
        they don't have to be your future character's name.  When your account
        has been created, you will create a character.  Your account can host five characters.

        Enter your new username:
    """.strip("\n"))
    options = (
        {
            "key": "_default",
            "desc": "Enter your new username.",
            "goto": "create_username",
        },
    )
    return text, options

def create_username(caller, input):
    """Prompt to enter a valid username (one that doesnt exist).

    'input' contains the new username.  If it exists, prompt
    the username to retry or go back to the login screen.

    """
    input = input.strip()
    accounts = Account.objects.filter(username__iexact=input)
    account = accounts[0] if accounts else None
    options = (
        {
            "key": "_default",
            "desc": "Enter your new account's password.",
            "goto": "create_password",
        },
    )

    # If an account with that name exists, a new one will not be created
    if account:
        text = dedent("""
            |rThe account {} already exists.|n
                Type |wb|n to go back to the login screen.
                Or enter another username to create.
        """.strip("\n")).format(input)

        # Loops on the same node
        options = (
            {
                "key": "b",
                "desc": "Go back to the login screen..",
                "goto": "pre_start",
            },
            {
                "key": "_default",
                "desc": "Enter another username.",
                "goto": "create_username",
            },
        )
    elif not RE_VALID_USERNAME.search(input):
        text = dedent("""
            |rThis username isn't valid.|n
            Letters, numbers, the underscore sign (_) and the dot (.)
            are accepted in your username.  Additionally, the username must
            be at least 3 characters long.
                Type |wb|n to go back to the login screen.
                Or enter another username to be created.
        """.strip("\n"))
        options = (
            {
                "key": "b",
                "desc": "Go back to the login screen.",
                "goto": "pre_start",
            },
            {
                "key": "_default",
                "desc": "Enter another username.",
                "goto": "create_username",
            },
        )
    else:
        # We don't create the account right away, so we store its name
        caller.db._accountname = input

        # Disables echo to enter the password
        caller.msg(echo=False)

        # Redirects to the creation of a password
        text = "Enter this account's new password."
        options = (
            {
                "key": "_default",
                "desc": "Enter this account's new password.",
                "goto": "create_password",
            },
        )

    return text, options

def create_password(caller, input):
    """Ask the user to create a password.

    This node creates and validates a new password for this
    account.  It then follows up with the confirmation
    (confirm_password).

    """
    text = ""
    options = (
        {
            "key": "b",
            "desc": "Go back to the login screen.",
            "goto": "pre_start",
        },
        {
            "key": "_default",
            "desc": "Enter your password.",
            "goto": "create_password",
        },
    )

    password = input.strip()
    accountname = caller.db._accountname
    if len(password) < LEN_PASSWD:
        # The password is too short
        text = dedent("""
            |rYour password must be at least {} characters long.|n
                Type |wb|n to return to the login screen.
                Or enter another password.
        """.strip("\n")).format(LEN_PASSWD)
    else:
        # Redirects to the "confirm_passwrod" node
        caller.db._password = sha256(password).hexdigest()
        text = "Enter your password again."
        options = (
            {
                "key": "_default",
                "desc": "Enter the passwod again.",
                "goto": "confirm_password",
            },
        )

    return text, options

def confirm_password(caller, input):
    """Ask the user to confirm the account's password.

    The account's password has been saved in the session for the
    time being, as a hashed version.  If the hashed version of
    the retyped password matches, then the account is created.
    If not, ask for another password.

    """
    text = ""
    options = (
        {
            "key": "_default",
            "desc": "Enter your password.",
            "goto": "create_password",
        },
    )

    password = input.strip()

    accountname = caller.db._accountname
    first_password = caller.db._password
    second_password = sha256(password).hexdigest()
    if first_password != second_password:
        text = dedent("""
            |rThe password you have specified doesn't match the first one.|n

            Enter a new password for this account.
        """.strip("\n"))
    else:
        # Creates the new account.
        caller.msg(echo=True)
        try:
            permissions = settings.PERMISSION_ACCOUNT_DEFAULT
            account = _create_account(caller, accountname,
                    password, permissions)
        except Exception:
            # We are in the middle between logged in and -not, so we have
            # to handle tracebacks ourselves at this point. If we don't, we
            # won't see any errors at all.
            caller.msg(dedent("""
                |rAn error occurred.|n  Please email an admin if
                the problem persists.

                Please enter another password.
            """.strip("\n")))
            logger.log_trace()
        else:
            caller.db._account = account
            del caller.db._password
            text = "Your new account was successfully created!"
            text += "\n\n" + _text_email_address(account)
            options = (
                {
                    "key": "_default",
                    "desc": "Enter a valid email address.",
                    "goto": "email_address",
                },
            )

    return text, options

def email_address(caller, input):
    """Prompt the user to enter a valid email address."""
    text = ""
    options = (
        {
            "key": "_default",
            "desc": "Enter a valid email address.",
            "goto": "email_address",
        },
    )

    email_address = input.strip()
    account = caller.db._account

    # Search for accounts with an identical email address
    identical = list(Account.objects.filter(email__iexact=email_address))

    if account in identical:
        identical.remove(account)

    # Try to validate the email address
    try:
        validate_email(email_address)
    except ValidationError:
        valid = False
    else:
        valid = True

    if not valid:
        # The email address doesn't seem to be valid
        text = dedent("""
            |rSorry, the specified email address {} cannot be accepted as a valid one.|n

            Please enter another email address.
        """.strip("\n")).format(email_address)
    elif identical:
        # The email address is already used
        text = dedent("""
            |rThe email address you have entered is already being used by another account.

            Please enter another email address.
        """.strip("\n"))
    else:
        account.email = email_address
        account.save()

        # Generates the 4-digit validation code
        numbers = "012345678"
        code = ""
        for i in range(4):
            code += choice(numbers)

        # Sends an email with the code
        subject = "[Avenew] Account validation"
        body = dedent("""
            You have successfully created the account {} on Avenew.

            In order to validate it and begin to play, you need to enter the following four-digit
            code in your MUD client.  If you have been disconnected, just login again, entering
            your account's name and password, the validation screen will appear.

            Four-digit code: {}
        """.strip("\n")).format(account.name, code)
        recipient = email_address
        account.db.valid = False
        account.db.validation_code = code
        try:
            assert not settings.TEST_SESSION
            send_email("NOREPLY", recipient, subject, body, store=False)
        except AssertionError:
            account.db.valid = True
            account.attributes.remove("validation_code")
            caller.msg(dedent("""
                Avenew is in a test session mode, your account has been validated automatically.
            """.strip("\n")).format(email_address))
            caller.msg("-----  You will now create the first character of this account. -----")
            _login(caller, account)
            text = ""
            options = (
                {
                    "key": "_default",
                    "desc": "Enter your new character's first name.",
                    "goto": "create_first_name",
                },
            )
        except (SMTPException, socket.error):
            # The email could not be sent
            account.db.valid = True
            account.attributes.remove("validation_code")
            caller.msg(dedent("""
                Avenew couldn't send your email containing your validation code to {}.
                This is probably due to Avenew's failure to connect to the SMTP server.
                Your account has been validated automatically.
            """.strip("\n")).format(email_address))
            caller.msg("-----  You will now create the first character of this account. -----")
            _login(caller, account)
            text = ""
            options = (
                {
                    "key": "_default",
                    "desc": "Enter your new character's first name.",
                    "goto": "create_first_name",
                },
            )
        else:
            text = dedent("""
                An email has been sent to {}.  It contains your validation code which you'll need in
                order to finish creating your account.  If you haven't received the validation email
                after some minutes have passed, check your spam folder to see if it's inside of it.
                If not, you might want to select another email address, or contact an Avenew administrator.

                From here you can:
                    Type |wb|n to choose a different email address.
                    Enter your 4-digit validation code.
                """.strip("\n")).format(email_address)
            options = (
                {
                    "key": "b",
                    "desc": "Go back to the email address selection.",
                    "goto": "pre_email_address",
                },
                {
                    "key": "_default",
                    "desc": "Enter your validation code.",
                    "goto": "validate_account",
                },
            )

    return text, options

def validate_account(caller, input):
    """Prompt the user to enter the received validation code."""
    text = ""
    options = (
        {
            "key": "b",
            "desc": "Go back to the email address menu.",
            "goto": "pre_email_address",
        },
        {
            "key": "_default",
            "desc": "Enter the validation code.",
            "goto": "validate_account",
        },
    )

    account = caller.db._account
    if account.db.validation_code != input.strip():
        text = dedent("""
            |rSorry, the specified validation code {} doesn't match the one stored for this account.
            Is it the code you received by email?  You can try to enter it again,
            Or enter |wb|n to choose a different email address.
        """.strip("\n")).format(input.strip())
    else:
        account.db.valid = True
        account.attributes.remove("validation_code")
        account.record_email_address()
        caller.msg("-----  You will now create the first character of this account. -----")
        _login(caller, account)
        text = ""
        options = (
            {
                "key": "_default",
                "desc": "Enter your new character's first name.",
                "goto": "create_first_name",
            },
        )

    return text, options

## Transition nodes
def pre_start(self):
    """Node to redirect to 'start'."""
    text = "Enter your username or |wNEW|n to create an account."
    options = (
        {
            "key": "new",
            "desc": "Create a new character.",
            "goto": "create_account",
        },
        {
            "key": "_default",
            "desc": "Login to an existing account.",
            "goto": "username",
        },
    )
    return text, options

def pre_email_address(self):
    """Node to redirect to 'email_address'."""
    text = "Enter another valid email address."
    options = (
        {
            "key": "_default",
            "desc": "Enter a valid email address.",
            "goto": "email_address",
        },
    )
    return text, options

## Private functions
def _create_account(session, accountname, password, permissions, typeclass=None, email=None):
    """
    Helper function, creates an account of the specified typeclass.


    Contrary to the default `evennia.commands.default.unlogged._create_account`,
    the account isn't connected to the public chaannel.

    """
    try:
        new_account = create.create_account(accountname, email, password, permissions=permissions, typeclass=typeclass)

    except Exception as e:
        session.msg("There was an error creating the Account:\n%s\n If this problem persists, contact an admin." % e)
        logger.log_trace()
        return False

    # This needs to be set so the engine knows this account is
    # logging in for the first time. (so it knows to call the right
    # hooks during login later)
    new_account.db.FIRST_LOGIN = True
    return new_account

def _text_email_address(account):
    """Return the text for the email address menu node."""
    text = dedent("""
        Enter a valid email address for the account {}.

        An email confirmation will be sent to this address with a 4-digit code that you will have
        to enter to validate this account.  This email address will be used only by the staff,
        should the need arise.  You will be able to update this email address
        if desired.

        Enter your email address.
    """.strip("\n")).format(account.name)

    return text

def _wrong_password(account):
    """Function called after the 3 seconds are up, when a wrong password has been supplied."""
    account.db._locked = False
    account.msg("Enter your password again.")


class AccountMenu(evmenu.EvMenu):

    """Menu for login into an account or creating an account."""

    def __init__(self, caller):
        super(AccountMenu, self).__init__(caller, "menu.account", startnode="start", auto_quit=False,
                cmd_on_exit=None)

    def node_formatter(self, nodetext, optionstext):
        """
        Formats the entirety of the node.

        Args:
            nodetext (str): The node text as returned by `self.nodetext_formatter`.
            optionstext (str): The options display as returned by `self.options_formatter`.
            caller (Object, Account or None, optional): The caller of the node.

        Returns:
            node (str): The formatted node to display.

        """
        return nodetext
