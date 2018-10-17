# -*- coding: utf-8 -*-

"""
At_initial_setup module template

Custom at_initial_setup method. This allows you to hook special
modifications to the initial server startup process. Note that this
will only be run once - when the server starts up for the very first
time! It is called last in the startup process and can thus be used to
overload things that happened before it.

The module must contain a global function at_initial_setup().  This
will be called without arguments. Note that tracebacks in this module
will be QUIETLY ignored, so make sure to check it well to make sure it
does what you expect it to.

"""

from evennia import AccountDB

try:
    from server.conf.secret_at_initial_setup import secret_setup
except ImportError:
    secret_setup = None

from typeclasses.rooms import Room
from world.log import main

def at_initial_setup():
    """
    Function called at initial_setup.

    This function makes sure account#1 (the superuser) is valid.

    """
    try:
        account = AccountDB.objects.get(id=1)
        account.db.valid = True

        # Set the central room
        room = Room.objects.get(id=2)
        room.x = 0
        room.y = 0
        room.z = 2
        room.ident = "central"

        if secret_setup:
            secret_setup()
    except Exception:
        main.exception("An error occurred at initial setup.")
    else:
        main.info("Successful at initial setup")
