"""
This module contains the 'validate_account' menu node.

"""

from textwrap import dedent

from menu.character import _options_choose_characters

def validate_account(caller, input):
    """Prompt the user to enter the received validation code."""
    text = ""
    options = (
        {
            "key": "b",
            "desc": "Go back to the e-mail address menu.",
            "goto": "email_address",
        },
        {
            "key": "_default",
            "desc": "Enter the validation code.",
            "goto": "validate_account",
        },
    )

    player = caller.db._player
    if player.db.validation_code != input.strip():
        text = dedent("""
            |rSorry, the specified validation code {} doesn't match
            the one stored for this account.  Is it the code you
            received by e-mail?  You can try to enter it again, or
            enter |yb|n to choose a different e-mail address.
        """.strip("\n")).format(input.strip())
    else:
        player.db.valid = True
        player.attributes.remove("validation_code")
        text = ""
        options = _options_choose_characters(player)

    return text, options
