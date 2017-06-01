"""
This module contains the 'confirm_password' menu node.

"""

from hashlib import sha256
from textwrap import dedent

from django.conf import settings

from evennia import logger

from menu.character import _login
from menu.email_address import text_email_address

def confirm_password(caller, input):
    """Ask the user to confirm the account's password.

    The account's password has been saved in the session for the
    time being, as a hashed version.  If the hashed version of
    the retyped password matches, then the player is created.
    If not, ask for another password.

    """
    text = ""
    options = (
        {
            "key": "b",
            "desc": "Go back to the password selection.",
            "goto": "create_password",
        },
        {
            "key": "_default",
            "desc": "Enter your password.",
            "goto": "confirm_password",
        },
    )

    caller.msg(echo=True)
    password = input.strip()

    playername = caller.db._playername
    first_password = caller.db._password
    second_password = sha256(password).hexdigest()
    if first_password != second_password:
        text = dedent("""
            |rThe password you have specified doesn't match the first one.|n
                Type |yb|n to choose a different password.
                Or type the confirmation password again.
        """.strip("\n"))
    else:
        # Creates the new player.
        from evennia.commands.default import unloggedin
        try:
            permissions = settings.PERMISSION_PLAYER_DEFAULT
            player = unloggedin._create_player(caller, playername,
                    password, permissions)
        except Exception:
            # We are in the middle between logged in and -not, so we have
            # to handle tracebacks ourselves at this point. If we don't, we
            # won't see any errors at all.
            caller.msg(dedent("""
                |rAn error occurred.|n  Please e-mail an admin if
                the problem persists.
                    Type |yb|n to go back to the login screen.
                    Or enter another password.
            """.strip("\n")))
            logger.log_trace()
        else:
            caller.db._player = player
            del caller.db._password
            _login(caller, player)
            text = "Your new account was successfully created!"
            text += "\n\n" + text_email_address(player)
            options = (
                {
                    "key": "_default",
                    "desc": "Enter a valid e-mail address.",
                    "goto": "email_address",
                },
            )

    return text, options
