"""
This module contains the 'username' node menu.

"""

from textwrap import dedent

from typeclasses.players import Player

def username(caller, input):
    """Check that the username leads to an existing player.

    Check that the specified username exists.  If the username doesn't
    exist, display an error message and ask the user to either
    enter 'b' to go back, or to try again.
    If it does exist, move to the next node (enter password).

    """
    input = input.strip()
    players = Player.objects.filter(username__iexact=input)
    player = players[0] if players else None
    if player is None:
        text = dedent("""
            |rThe username {} doesn't exist yet.  Have you created it?|n
                Type |yb|n to go back to the previous menu.
                Or try another name.
        """.strip("\n")).format(input)
        options = (
            {
                "key": "b",
                "desc": "Go back to the login screen.",
                "goto": "start",
            },
            {
                "key": "_default",
                "desc": "Try again.",
                "goto": "username",
            },
        )
    else:
        caller.db._player = player
        locked = player.db._locked

        # The player is temporarily locked when a wrong password
        # has been supplied.  This lock shouldn't last more than
        # 3 seconds.
        if locked:
            text = "Please wait..."
            scripts = player.scripts.get("wrong_password")
            if scripts:
                script = scripts[0]
                script.db.session = caller
            else:
                print "Cannot retrieve the 'wrong_password' script."
        else:
            text = "Enter the password for the account {}.".format(
                    player.name)

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
