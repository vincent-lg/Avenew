"""
This module contains the 'create_username' node menu.

"""

import re
from textwrap import dedent

from typeclasses.players import Player

## Constants
RE_VALID_USERNAME = re.compile(r"^[a-z0-9_.]{3,}$", re.I)

def create_username(caller, input):
    """Prompt to enter a valid username (one that doesnt exist).

    'input' contains the new username.  If it exists, prompt
    the username to retry or go back to the login screen.

    """
    input = input.strip()
    players = Player.objects.filter(username__iexact=input)
    player = players[0] if players else None
    options = (
        {
            "key": "_default",
            "desc": "Enter your new account's password.",
            "goto": "create_password",
        },
    )

    # If a player with that name exists, a new one will not be created
    if player:
        text = dedent("""
            |rThe account {} already exists.|n
                Type |yb|n to go back to the login screen.
                Or enter another username to create.
        """.strip("\n")).format(input)
        # Loops on the same node
        options = (
            {
                "key": "b",
                "desc": "Go back to the login screen.",
                "goto": "start",
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
                Type |yb|n to go back to the login screen.
                Or enter another username to be created.
        """.strip("\n"))
        options = (
            {
                "key": "b",
                "desc": "Go back to the login screen.",
                "goto": "start",
            },
            {
                "key": "_default",
                "desc": "Enter another username.",
                "goto": "create_username",
            },
        )
    else:
        # We don't create the player right away, so we store its name
        caller.db._playername = input
        # Disables echo for entering password
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
