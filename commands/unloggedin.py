"""
A login menu using EvMenu.

Contribution - Vincent-lg 2016

This module defines a simple login system, similar to the one
defined in 'menu_login.py".  This present menu system, however,
uses EvMenu (hence the name).  This module contains the
functions (nodes) of the menu, with the CmdSet and
UnloggedCommand called when a user logs in.  In other words,
instead of using the 'connect' or 'create' commands once on the
login screen, players have to navigate through a simple menu
asking them to enter their username (then password), or to type
'new' to create one.  You may want to update your login screen
if you use this system.

When you'll reload the server, new sessions will connect to the
new login system, where they will be able to:

* Enter their username, assuming they have an existing player.
* Enter 'NEW' to create a new player.

The top-level functions in this file are menu nodes (as
described in EvMenu).  Each one of these functions is
responsible for prompting the user with a specific information
(username, password and so on).  At the bottom of the file are
defined the CmdSet for Unlogging users, which adds a new command
(defined below) that is called just after a new session has been
created, in order to create the menu.  See the specific
documentation on functions (nodes) to see what each one should
do.

"""

from evennia import Command, CmdSet
from evennia import syscmdkeys
from evennia.utils.evmenu import EvMenu

from menu.confirm_password import confirm_password
from menu.create_account import create_account
from menu.create_password import create_password
from menu.create_username import create_username
from menu.email_address import email_address
from menu.generic import _formatter, _input_no_digit
from menu.password import password
from menu.start import start
from menu.username import username
from menu.validate_account import validate_account

class UnloggedinCmdSet(CmdSet):
    "Cmdset for the unloggedin state"
    key = "DefaultUnloggedin"
    priority = 0

    def at_cmdset_creation(self):
        "Called when cmdset is first created."
        self.add(CmdUnloggedinLook())


class CmdUnloggedinLook(Command):
    """
    An unloggedin version of the look command. This is called by the server
    when the player first connects. It sets up the menu before handing off
    to the menu's own look command.
    """
    key = syscmdkeys.CMD_LOGINSTART
    locks = "cmd:all()"
    arg_regex = r"^$"

    def func(self):
        "Execute the menu"
        nodes = {
                "start": start,
                "username": username,
                "password": password,
                "create_account": create_account,
                "create_username": create_username,
                "create_password": create_password,
                "confirm_password": confirm_password,
                "email_address": email_address,
                "validate_account": validate_account,
        }

        menu = EvMenu(self.caller, nodes, startnode="start", auto_quit=False,
                cmd_on_exit=None, node_formatter=_formatter,
                input_parser=_input_no_digit, persistent=True)
