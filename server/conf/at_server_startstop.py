"""
Server startstop hooks

This module contains functions called by Evennia at various
points during its startup, reload and shutdown sequence. It
allows for customizing the server operation as desired.

This module must contain at least these global functions:

at_server_start()
at_server_stop()
at_server_reload_start()
at_server_reload_stop()
at_server_cold_start()
at_server_cold_stop()

"""

import pdb
import subprocess
import sys

from evennia import TICKER_HANDLER as ticker_handler

from services import email
import tickers

def at_server_start():
    """
    This is called every time the server starts up, regardless of
    how it was shut down.
    """
    # Setup the email service
    email.setup()

    # Launch tickers
    ticker_handler.add(3, tickers.vehicles.move)



def at_server_stop():
    """
    This is called just before the server is shut down, regardless
    of it is for a reload, reset or shutdown.
    """
    pass


def at_server_reload_start():
    """
    This is called only when server starts back up after a reload.
    """
    pass


def at_server_reload_stop():
    """
    This is called only time the server stops before a reload.
    """
    # Pull the Git repository
    print "Pulling from Github..."
    process = subprocess.Popen("git pull", shell=True)
    process.wait()


def at_server_cold_start():
    """
    This is called only when the server starts "cold", i.e. after a
    shutdown or a reset.
    """
    pass


def at_server_cold_stop():
    """
    This is called only when the server goes down due to a shutdown or
    reset.
    """
    pass
