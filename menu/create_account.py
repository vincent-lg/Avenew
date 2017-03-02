"""
This module contains the 'create_account' node menu.

"""

from textwrap import dedent

def create_account(caller):
    """Create a new account.

    This node simply prompts the user to enter a username.
    The input is redirected to 'create_username'.

    """
    text = "Enter your new account's name."
    options = (
        {
            "key": "_default",
            "desc": "Enter your new username.",
            "goto": "create_username",
        },
    )
    return text, options
