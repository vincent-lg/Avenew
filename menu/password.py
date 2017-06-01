"""
This module contains the 'password' node menu.

"""

from textwrap import dedent

from evennia.server.models import ServerConfig

from menu.character import (
        _text_choose_characters,
        _options_choose_characters,
        _login)
from menu.email_address import text_email_address
from typeclasses.scripts import WrongPassword

## Constants
LEN_PASSWD = 6

def password(caller, input):
    """Ask the user to enter the password to this player.

    This is assuming the user exists (see 'create_username' and
    'create_password').  This node "loops" if needed:  if the
    user specifies a wrong password, offers the user to try
    again or to go back by entering 'b'.
    If the password is correct, then login.

    """
    caller.msg(echo=True)
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
    player = caller.db._player
    # If the account is locked, the user has to wait (maximum
    # 3 seconds) before retrying
    if player.db._locked:
        text = "|gPlease wait, you cannot enter your password yet.|n"
        return text, options

    caller.msg(echo=True)
    bans = ServerConfig.objects.conf("server_bans")
    banned = bans and (any(tup[0] == player.name.lower() for tup in bans) \
            or any(tup[2].match(caller.address) for tup in bans if tup[2]))

    if not player.check_password(input):
        caller.msg(echo=False)
        text = dedent("""
            |rIncorrect password.|n
                Type |yb|n to go back to the login screen.
                Or wait 3 seconds before trying a new password.
        """.strip("\n"))

        # Loops on the same node
        player.scripts.add(WrongPassword)
        scripts = player.scripts.get("wrong_password")
        if scripts:
            script = scripts[0]
            script.db.session = caller
        else:
            print "Cannot retrieve the 'wrong_password' script."

        options = (
            {
                "key": "b",
                "desc": "Go back to the login screen.",
                "goto": "start",
            },
            {
                "key": "_default",
                "desc": "Enter your password again.",
                "goto": "password",
            },
        )
    elif banned:
        # This is a banned IP or name!
        string = dedent("""
            |rYou have been banned and cannot continue from here.|n
            If you feel this ban is in error, please email an admin.
        """.strip("\n"))
        caller.msg(string)
        caller.sessionhandler.disconnect(
                caller, "Good bye!  Disconnecting...")
    else:
        # The password is correct, we can log into the player.
        if not player.email:
            # Redirects to the node to set an e-mail address
            text = text_email_address(player)
            options = (
                {
                    "key": "_default",
                    "desc": "Enter your e-mail address.",
                    "goto": "email_address",
                },
            )
        elif not player.db.valid:
            # Redirects to the node for the validation code
            text = "Enter your received validation code."
            options = (
                {
                    "key": "_default",
                    "desc": "Enter your validation code.",
                    "goto": "validate_account",
                },
            )
        else:
            _login(caller, player)
            text = ""
            options = _options_choose_characters(player)

    return text, options
