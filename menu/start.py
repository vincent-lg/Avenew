"""
This module contains the 'welcome' node menu.

"""

from django.conf import settings

from evennia.utils.utils import random_string_from_module

## Constants
CONNECTION_SCREEN_MODULE = settings.CONNECTION_SCREEN_MODULE

def start(caller):
    """The user should enter his/her username or NEW to create one.

    This node is called at the very beginning of the menu, when
    a session has been created OR if an error occurs further
    down the menu tree.  From there, users can either enter a
    username (if this username exists) or type NEW (capitalized
    or not) to create a new player.

    """
    text = random_string_from_module(CONNECTION_SCREEN_MODULE)
    text += "\n\nEnter your username or |yNEW|n to create an account."
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
