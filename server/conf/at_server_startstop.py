# -*- coding: utf-8 -*-

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

import os
import subprocess
import sys

from evennia import TICKER_HANDLER as ticker_handler
from evennia import ScriptDB, create_script

from auto.types.high_tech import load_apps
import tickers
from world.log import begin, end, main, app

def at_server_start():
    """
    This is called every time the server starts up, regardless of
    how it was shut down.
    """
    # Start the main logger
    begin()

    # Affect default encoding (it's a security on frozen versions)
    if getattr(sys, "frozen", False):
        main.info("Running in frozen mode, try to change the default encoding")
        try:
            sys.setdefaultencoding("utf-8")
        except Exception:
            main.exception("An error occured while changing encoding.")
        else:
            main.info("Setting defaultencoding to utf-8")

    # Launch the script if it's not running
    try:
        script = ScriptDB.objects.get(db_key="event_handler")
    except ScriptDB.DoesNotExist:
        script = create_script("typeclasses.scripts.AvEventHandler")
        main.info("Creating the EventHandler")

    # Launch tickers
    ticker_handler.add(3, tickers.vehicles.move)

    # Load the apps
    errors = load_apps()
    for name, error in errors:
        app.warning("Error while loading {}: {}".format(name, error))

def at_server_stop():
    """
    This is called just before the server is shut down, regardless
    of it is for a reload, reset or shutdown.
    """
    end()


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
    current = os.getcwd()
    if os.path.exists("../evennia"):
        print("Evennia seems to exist, try to pull from it", current)
        os.chdir("../evennia")
        process = subprocess.Popen("git pull", shell=True)
        process.wait()
        os.chdir(current)
    else:
        print("Evennia doesn't exist, don't pull from it.")

    print("Pulling Avenew from Github...")
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
