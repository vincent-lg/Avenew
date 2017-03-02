"""
This module contains the 'create_password' menu node.

"""

from hashlib import sha256
from textwrap import dedent

from menu.password import LEN_PASSWD

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
            "goto": "start",
        },
        {
            "key": "_default",
            "desc": "Enter your password.",
            "goto": "create_password",
        },
    )

    password = input.strip()
    playername = caller.db._playername
    if len(password) < LEN_PASSWD:
        # The password is too short
        text = dedent("""
            |rYour password must be at least {} characters long.|n
                Type |yb|n to return to the login screen.
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
