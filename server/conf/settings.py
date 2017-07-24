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
SERVERNAME = "Avenew One"

######################################################################
# Django web features
######################################################################


# Activate SSL protocol (SecureSocketLibrary)
SSL_ENABLED = True

# IRC
IRC_ENABLED = True

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

# Channel options
CHANNEL_COMMAND_CLASS = "commands.comms.ChannelCommand"

# Screen reader and accessibility options
SCREENREADER_REGEX_STRIP = r"\+-+|\+$|\+~|---+|~~+|==+"

# Web
INSTALLED_APPS += (
        'django.contrib.humanize',
        'django_nyt',
        'mptt',
        'sekizai',
        'sorl.thumbnail',
        'wiki',
        'wiki.plugins.attachments',
        'wiki.plugins.notifications',
        'wiki.plugins.images',
        'wiki.plugins.macros',
        "web.help_system",
)

SITE_ID = 1

WIKI_ACCOUNT_HANDLING = True
WIKI_ACCOUNT_SIGNUP_ALLOWED = True

TEMPLATES[0]['OPTIONS']['context_processors'] += ['sekizai.context_processors.sekizai']

def is_superuser(article, user):
    """Return True if user is a superuser, False otherwise."""
    return not user.is_anonymous() and user.is_superuser

def is_builder(article, user):
    """Return True if user is a builder, False otherwise."""
    return not user.is_anonymous() and user.locks.check_lockstring(user, "perm(Builders)")

WIKI_CAN_ASSIGN = is_superuser
WIKI_CAN_ASSIGN_OWNER = is_superuser
WIKI_CAN_CHANGE_PERMISSIONS = is_superuser
WIKI_CAN_DELETE = is_builder
WIKI_CAN_MODERATE = is_superuser
WIKI_CAN_READ = is_builder
WIKI_CAN_WRITE = is_builder

try:
    from server.conf.secret_settings import *
except ImportError:
    pass
