# -*- coding: utf-8 -*-

r"""
Evennia settings file.

The available options are found in the default settings file found
here:

c:\users\vincent\evennia\evennia\settings_default.py

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "Avenew One"

######################################################################
# Django web features
######################################################################

## Commands
# UnloggedinCmdSet
CMDSET_UNLOGGEDIN = "commands.unloggedin.UnloggedinCmdSet"
DELAY_CMD_LOGINSTART = 0

# Default prefix
CMD_IGNORE_PREFIXES = "@:"

# Default command class
COMMAND_DEFAULT_CLASS = "commands.command.MuxCommand"

# Multi-session mode : 2
# One account, multiple character, only one session per character
MULTISESSION_MODE = 2

# Time factor
TIME_FACTOR = 4

# Time configuration
TIME_ZONE = "America/Los_Angeles"
TIME_GAME_EPOCH = 1577865600

# Channel options
CHANNEL_COMMAND_CLASS = "commands.comms.ChannelCommand"

# Screen reader and accessibility options
SCREENREADER_REGEX_STRIP = r"\+-+|\+$|\+~|---+|~~+|==+"

# Search settings
SEARCH_MULTIMATCH_REGEX = r"(?P<number>[0-9]+)\.(?P<name>.*)"
SEARCH_MULTIMATCH_TEMPLATE = "  {number}.{name}{aliases}{info}\n"

## Web
INSTALLED_APPS += (
        "anymail",
        "evennia_wiki",
        "web.builder",
        "web.evapp",
        "web.help_system",
        "web.mailgun",
        "web.text",
)

## Communication
TEST_SESSION = False
BATCH_DIR = r"C:\Users\Vincent Le Goff\Dropbox\Avenew one\Quartiers"

# Language options
USE_I18N = True
LANGUAGE_CODE = 'fr'
ENCODINGS = ["latin-1", "utf-8", "ISO-8859-1"]

# Private settings
try:
    from server.conf.secret_settings import *
except ImportError:
    pass
