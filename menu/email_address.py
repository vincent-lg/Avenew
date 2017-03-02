"""
This module contains the 'email_address' menu node.

"""

from random import choice
from textwrap import dedent

from services import email
from typeclasses.players import Player

def email_address(caller, input):
    """Prompt the user to enter a valid email address."""
    text = ""
    options = (
        {
            "key": "b",
            "desc": "Go back to the login screen.",
            "goto": "start",
        },
        {
            "key": "_default",
            "desc": "Enter a valid e-mail address.",
            "goto": "email_address",
        },
    )

    email_address = input.strip()
    player = caller.db._player

    # Search for players with an identical e-mail address
    identical = list(Player.objects.filter(email=email_address))

    if player in identical:
        identical.remove(player)

    if not email.is_email_address(email_address):
        # The e-mail address doesn't seem to be valid
        text = dedent("""
            |rSorry, the specified e-mail address {} cannot be
            accepted as a valid one.|n  You can:
                Type |yb|n to return to the login screen.
                Or enter another e-mail address.
        """.strip("\n")).format(email_address)
    elif identical:
        # The e-mail address is already used
        text = dedent("""
            |rThe e-mail address you have entered is already being used
            by another account.  You can either:
                Type |yb|n to return to the login screen.
                Or enter another e-mail address.
        """.strip("\n"))
    else:
        player.email = email_address
        player.save()

        # Generates the 4-digit validation code
        numbers = "012345678"
        code = ""
        for i in range(4):
            code += choice(numbers)

        # Sends an e-mail with the code
        subject = "Account validation"
        body = dedent("""
            You have successfully created the account {} on that MUD.

            In order to validate it and begin to play, you need to
            enter the following four-digit code in your MUD client.
            If you have been disconnected, just login again, entering
            your account's name and password, the validation screen
            will be displayed.

            Four-digit code: {}
        """.strip("\n")).format(player.name, code)
        recipent = email_address
        error = "The account {}'s validation code is {}.".format(
                player.name, code)
        player.db.valid = False
        player.db.validation_code = code
        email.send("team@no-host.com", recipent, subject, body, error)
        text = dedent("""
            An email has been sent to {}.  It contains your validation
            code which you'll need to finish creating your account.
            If you haven't received the validation e-mail after some
            minutes have passed, check your spam folder to see if
            it's inside.  If not, you might try to select
            another e-mail address, or contact an administrator.

            From here you can:
                Type |yb|n to choose a different e-mail address.
                Enter your received confirmation code.
            """.strip("\n")).format(email_address)
        options = (
            {
                "key": "b",
                "desc": "Go back to the e-mail address selection.",
                "goto": "email_address",
            },
            {
                "key": "_default",
                "desc": "Enter your validation code.",
                "goto": "validate_account",
            },
        )

    return text, options

def text_email_address(player):
    """Return the text for the email-address menu node."""
    text = dedent("""
        Enter a valid e-mail address for the account {}.

        An e-mail confirmation will be sent to this address with a
        four-digit code that you will have to enter to validate this
        account.  This e-mail address will be used only by the staff,
        if needed.  You will be able to update this e-mail address if
        desired.

        Enter your email address.
    """.strip("\n")).format(player.name)

    return text
