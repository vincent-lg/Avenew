"""
High-tech device types.
"""

import os

from evennia.utils.utils import all_from_module, lazy_property
from evennia.contrib.random_string_generator import RandomStringGenerator

from auto.apps.base import BaseApp, MainScreen
from auto.types.base import BaseType

## Constants
PHONE_GENERATOR = RandomStringGenerator("phone number", r"[0-9]{3}-[0-9]{4}")
APPS = {}

## Functions
def load_apps(path="auto.apps", errors=None):
    """Dynamically-load the apps stored in modules."""
    errors = errors or []
    relpath = path.replace(".", os.path.sep)
    for content in os.listdir(relpath):
        if content == "base.py":
            continue

        if os.path.isfile(relpath + os.path.sep + content) and content.endswith(".py") and not content.startswith("_"):
            # Obviously a module, try to load it
            try:
                variables = all_from_module(path + "." + content[:-3])
            except Exception as err:
                errors.append((path + "." + content[:-3], str(err)))
            else:
                # Explore the module, looking for a class
                app = None
                for var in variables.values():
                    if issubclass(var, BaseApp) and getattr(var, "app_name", ""):
                        app = var
                        break

                if not app:
                    errors.append((path + "." + content[:-3], "Could not find the application class"))
                else:
                    folder = getattr(app, "folder", "app")
                    if folder not in APPS:
                        APPS[folder] = {}
                    folder = APPS[folder]
                    app_name = app.app_name
                    folder[app_name] = app
        elif os.path.isdir(relpath + os.path.sep + content):
            # Explore the sub-folder
            load_apps(path + "." + content, errors)

    return errors

# Classes
class Phone(BaseType):

    """
    Definition of the phone type.

    A phone is an object that has a phone number, and can be reached
    through it.  It also supports several commands to phone, text,
    or do more advanced things.

    To create a smartphone (a phone with both the ability to text/phone
    and use apps), we combine the "phone" type with the "computer"
    type.  A computer has several applications it can use, and an
    object with both phone and computer type will be able to text and
    call from inside the computer interface.

    """

    name = "phone"

    def at_type_creation(self):
        """The type has just been added."""
        db = self.db
        if "number" not in db:
            number = PHONE_GENERATOR.get()
            db["number"] = number
            self.obj.tags.add(number.replace("-", ""), category="phone number")


class Computer(BaseType):

    """The computer type.
    
    A computer is an object that supports an interface with applications.
    A character with a computer can use it through the USE command,
    which will display an interface with the installed apps on this
    computer.

    Note that, in-game, a smartphone and a computer both share the same
    interface.  However, they might not have access to the same applications.
    A computer will probably be unable to text or phone (at least via
    the usual network, though a custom app could allow it) and will
    not be in constant connection with the Internet itself.

    """

    name = "computer"

    @lazy_property
    def apps(self):
        """Return the application handler."""
        return ApplicationHandler(self.obj, self)
    
    def at_type_creation(self):
        """The type has just been added.

        Since this method is only called for objects, we copy the prototype apps.

        """
        prototype = self.obj.db.prototype
        if prototype:
            type = prototype.types.get("computer")
            for folder, apps in type.db.get("apps", {}).items():
                for app in apps:
                    self.apps.add(app, folder=folder)

    def quit(self):
        """Quit the interface, removing the CmdSet if necessary."""
        db = self.db
        used = db.get("used")
        if used and used.cmdset.has("computer"):
            used.cmdset.delete("commands.high_tech.ComputerCmdSet")

        if used:
            del db["used"]

    def use(self, user):
        """Use the computer.

        This method creates a CmdSet on the user, if the computer isn't
        already used.  It also prepares the first screen.

        """
        db = self.db
        used = db.get("used")
        if used is user:
            user.msg("You already are using it.")
        elif used:
            user.msg("{} is already using it.".format(used.get_display_name(user)))
        elif user.cmdset.has("computer"):
            user.msg("It looks like you're already busy, isn't it?")
        else:
            # Add the CmdSet
            db["used"] = user
            user.cmdset.add("commands.high_tech.ComputerCmdSet", permanent=True)
            self.apps.load(user)
            screen = MainScreen(self.obj, user, self)
            screen._save()
            self.db["screen_tree"] = [("auto.apps.base.MainScreen", None, None)]
            screen.display()


class ApplicationHandler(object):

    """The application handler, containing apps.

    This handler, set on the computer type, allows to add and remove,
    install and uninstall applications.  The `AppHandler` (1type.apps`)
    is created right away, but individual applications are only created
    if the handler's `load` or `install` method is called.  In both
    cases, the user (the object using the computer) must be provided.

    """

    def __init__(self, obj, type):
        self.obj = obj
        self.type = type
        self._apps = []

    def __iter__(self):
        return iter(self._apps)

    def get(self, app_name, folder="app"):
        """
        Return an instanciated App object or None.

        This method looks into the instanciated App objects, that is,
        these that are loaded (with an active user).  It shouldn't be
        used to check an app is installed unless someone is currently
        using the phone (the handler has been loaded with an active user).

        Args:
            app_name (str): the name of the application to find.
            folder (str, optional): the name of the folder in which sits the app.

        Returns:
            app (App or None): the application, or None if not found.

        """
        for app in self._apps:
            if type(app).app_name == app_name and type(app).folder == folder:
                return app

        return None

    def add(self, app_name, folder="app"):
        """
        Add an application provided its name.

        This method can be used on a computer prototype (set on a
        prototype object) or an actualy computer (an object with
        this type).  Adding an app doesn't require a user.  When the
        computer will be used, the applications will be created with
        the proper user.  Application objects aren't created at this point.

        Args:
            app_name (str): the name of the application to add.

        Note:
            The order of added applications is kept, but it can easily
            be changed.

        """
        db = self.type.db
        if "apps" not in db:
            db["apps"] = {}
        apps = db["apps"]
        if folder not in apps:
            apps[folder] = []
        apps[folder].append(app_name)

    def load(self, user):
        """Load the apps, creating the App objects."""
        db = self.type.db
        folders = db.get("apps", {})
        for folder, apps in folders.items():
            for app_name in apps:
                AppClass = APPS.get(folder, {}).get(app_name, {})
                app = AppClass(self.obj, user, self.type)
                self._apps.append(app)

