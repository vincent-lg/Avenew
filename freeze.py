# Run this script to produce a frozen version of Evennia that can run Avenew
# You must be in the Virtual Environment (with evennia installed) to run this.

import os
import shutil
import sys
from textwrap import dedent

try:
    import evennia
except ImportError:
    print "evennia cannot be found on this Python path.  You should run this script from a Python environment where evennia is installed."
    sys.exit(1)

# Try to freeze evennia
print "Trying to freeze Evennia version", evennia.__version__

# First, call pyinstaller
status = os.system("pyinstaller avenew.spec -y")
print "Finished building avenew.exe with status", status
print "Copying the Evennia data..."
shutil.copytree("toevennia", "dist/avenew/evennia")
if os.path.exists("avenew"):
    shutil.rmtree("avenew")
print "Creating the frozen folder."
os.mkdir("avenew")
print "Placing the frozen executables in the frozen folder."
shutil.copytree("dist/avenew", "avenew/dist")
shutil.copy("twistd.exe", "avenew")

print "Copying the entire source code..."
for name in os.listdir(os.getcwd()):
    if name in ("avenew", "build", "dist", "toevennia", "avenew.py", "freeze.py") or name.startswith(".git") or any(name.endswith(ext) for ext in (".spec", ".bat", ".db")):
        continue

    if os.path.isfile(name):
        shutil.copy(name, "avenew")
    else:
        shutil.copytree(name, "avenew/" + name)

if os.path.exists("avenew/server/evennia.db3"):
    print "Removing the database."
    os.remove("avenew/server/evennia.db3")

# Change directory to frozen
os.chdir("avenew")

# Override a few sensitive files
print "Overriding settings..."
with open("server/conf/secret_settings.py", "w") as file:
    file.write(dedent('''
        # -*- coding: utf-8 -*-

        """Scret settings."""

        SECRET_KEY = 'bjqsznek!jj$m-5z9az)b)21(n)to3iu1vo)!rqlr@i5wf#-ki'

        # Enable DEBUG
        DEBUG = True

        TEST_SESSION = True

        # Protocols
        IRC_ENABLED = False
        SSL_ENABLED = False

        # Email configuration
        EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
        DEFAULT_FROM_EMAIL = "noreply@avenew.one"
        DNS_NAME = "avenew.one"

        ANYMAIL = {}

        # Outgoing email aliases
        OUTGOING_ALIASES = {}

        # Language options
        USE_I18N = True
        LANGUAGE_CODE = 'fr'
        ENCODINGS = ["latin-1", "utf-8", "ISO-8859-1"]
    ''').strip())

if os.path.exists("server/conf/secret_settings.pyc"):
    os.remove("server/conf/secret_settings.pyc")

with open("server/conf/secret_at_initial_setup.py", "w") as file:
    file.write(dedent('''
        # -*- coding: utf-8 -*-

        """
        secret_At_initial_setup module template

        Secret at_initial_setup method.

        """

        from django.conf import settings
        from evennia import ChannelDB, ObjectDB
        from evennia.utils import create

        def secret_setup():
            pass
    ''').strip())

if os.path.exists("server/conf/secret_at_initial_setup.pyc"):
    os.remove("server/conf/secret_at_initial_setup.pyc")

if os.path.exists("server/ssl.cert"):
    os.remove("server/ssl.cert")

if os.path.exists("server/ssl.key"):
    os.remove("server/ssl.key")

# Removing log files
for name in os.listdir("server/logs"):
    os.remove("server/logs/" + name)

print "Run migrations..."
os.system("evennia migrate")

# Redirect stdin
os.system("evennia createsuperuser")

# Create simple batch files
with open("start.bat", "w") as file:
    file.write(r"cmd /k dist\avenew.exe start")

with open("stop.bat", "w") as file:
    file.write(r"cmd /k dist\avenew.exe stop")

with open("avenew.bat", "w") as file:
    file.write(r"cmd /k dist\avenew.exe %*")

os.chdir("..")
