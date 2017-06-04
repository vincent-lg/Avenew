"""
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
SERVERNAME = "Even"

######################################################################
# Django web features
######################################################################


# The secret key is randomly seeded upon creation. It is used to sign
# Django's cookies. Do not share this with anyone. Changing it will
# log out all active web browsing sessions. Game web client sessions
# may survive.
SECRET_KEY = open("server/conf/secret.txt", "r").read()

# Activate SSL protocol (SecureSocketLibrary)
SSL_ENABLED = True

# UnloggedinCmdSet
CMDSET_UNLOGGEDIN = "commands.unloggedin.UnloggedinCmdSet"

# Multi-session mode : 2
# One account, multiple player, only one session per character
MULTISESSION_MODE = 2

# Time factor
TIME_FACTOR = 4

# Timezone
# Time configuration
TIME_ZONE = "America/Los_Angeles"
TIME_GAME_EPOCH = 1577865600


# Web
INSTALLED_APPS += (
        "web.help_system",
)

