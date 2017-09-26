"""
High-tech device types.
"""

import datetime
import os
from textwrap import dedent, wrap

from django.utils.timezone import make_aware
from evennia.utils import gametime
from evennia.utils.utils import all_from_module, class_from_module, crop, inherits_from, lazy_property, time_format
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

def return_appearance(type, looker, number=False, header=""):
    """Return the formatted appearance for a phone or computer."""
    phone_number = type.obj.tags.get(category="phone number")
    if not isinstance(phone_number, basestring):
        phone_number = "|gunset|n"
    else:
        phone_number = phone_number[:3] + "-" + phone_number[3:]

    date = datetime.datetime.fromtimestamp(gametime.gametime(absolute=True))
    text = dedent("""
        {header}


                                             {time}

                                 {date}
        """.strip("\n")).format(header=header,
                date=date.strftime("%A, %B {}, %Y".format(date.day)),
                time=date.strftime("%I:%M %p"),)

    # If a phone number, display it
    if number:
        text += "\n\n" + """
                                                                     {number}
        """.rstrip("\n").format(number=phone_number)

    # Display the notifications
    notifications = type.notifications.all()
    if notifications:
        text += "\n\n"
        for notification in notifications:
            title = crop(notification.title, 55, "...")
            content = "\n    ".join(wrap(notification.content, 74))
            text += "\n-   {:<55} ({})".format(title, notification.ago)
            if content:
                text += "\n    " + content

    return text

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

    @lazy_property
    def notifications(self):
        """Return the application handler."""
        return NotificationHandler(self.obj, self)

    @property
    def number(self):
        """Return the phone number of this object or None."""
        number = self.obj.tags.get(category="phone number")
        if not number or not isinstance(number, basestring):
            return None

        return number

    @property
    def prettu_number(self):
        """Return the pretty phone number (with the dash)."""
        number = self.number
        if number:
            number = number[:3] + "-" + number[3:]

        return number

    def at_type_creation(self):
        """The type has just been added."""
        db = self.db
        if "number" not in db:
            number = PHONE_GENERATOR.get()
            db["number"] = number
            self.obj.tags.add(number.replace("-", ""), category="phone number")

    def return_appearance(self, looker):
        """Return the appearance of the phone."""
        header = "AvenOS light 12.4"
        return return_appearance(self, looker, number=True, header=header)


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

    @lazy_property
    def notifications(self):
        """Return the application handler."""
        return NotificationHandler(self.obj, self)

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

    def return_appearance(self, looker):
        """Return the appearance of the phone."""
        header = "AvenOS 12.4            [6G]           [Bluetooth]           [96%}"
        number = True if self.obj.types.get("phone") else False
        return return_appearance(self, looker, number=number, header=header)

    def quit(self):
        """Quit the interface, removing the CmdSet if necessary."""
        db = self.db
        used = db.get("used")
        if used and used.cmdset.has("computer"):
            used.cmdset.remove("commands.high_tech.ComputerCmdSet")
            del used.db._aven_using

        if used:
            del db["used"]

        if "screen_tree" in db:
            del db["screen_tree"]

    def use(self, user, screen=None, app_name=None, folder="app", db=None):
        """Use the computer.

        This method creates a CmdSet on the user, if the computer isn't
        already used.  It also prepares the first screen.

        """
        used = self.db.get("used")
        if used is user:
            user.msg("You already are using it.")
        elif used:
            user.msg("{} is already using it.".format(used.get_display_name(user)))
        elif user.cmdset.has("computer"):
            user.msg("It looks like you're already busy, isn't it?")
        else:
            # Add the CmdSet
            self.apps.load(user)
            if app_name:
                app = self.apps.get(app_name, folder)
            else:
                app = None
            if screen:
                Screen = class_from_module(screen)
            else:
                Screen = MainScreen
            self.db["used"] = user
            user.cmdset.add("commands.high_tech.ComputerCmdSet", permanent=True)
            screen = Screen(self.obj, user, self, app)
            if "screen_tree" not in self.db:
                self.db["screen_tree"] = [(type(screen).__module__ + "." + type(screen).__name__, app_name, folder, db)]
            if db:
                screen.db.update(db)
            screen._save()
            screen.display()
            user.db._aven_using = self.obj


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
        # Delete all application objects
        self._apps[:] = []

        db = self.type.db
        folders = db.get("apps", {})
        for folder, apps in folders.items():
            for app_name in apps:
                AppClass = APPS.get(folder, {}).get(app_name, {})
                app = AppClass(self.obj, user, self.type)
                self._apps.append(app)


class NotificationHandler(object):

    """Notification handler, to handle giving notifications."""

    def __init__(self, obj, type):
        self.obj = obj
        self.type = type

    @lazy_property
    def db(self):
        """Return the DB for the notificaiton handler."""
        db = self.type.db
        if "notifications" not in db:
            db["notifications"] = []
        return db["notifications"]

    def all(self):
        """Return all notifications."""
        notifications = []
        for info in self.db:
            notification = Notification(**info)
            notification.obj = self.obj
            notification.handler = self
            notifications.append(notification)

        return notifications

    def add(self, title, screen, app, folder="app", content="", db=None):
        """Add a new notificaiton.

        Args:
            title (str): title of the notification to add.
            screen (str): screen path when addressing the notification.
            app (str): app name that sent the application.
            folder (str, optional): the folder containing the app.
            content (str, optional): the content of the notification.
            db (dict, optional): db attributes to give to the screen.
            alert (bool, optional): should we alert the location?

        """
        timestamp = gametime.gametime(absolute=True)
        kwargs = {
                "title": title,
                "screen": screen,
                "app": app,
                "folder": folder,
                "content": content,
                "db": db,
                "timestamp": timestamp,
        }
        notification = Notification(**kwargs)
        notification.obj = self.obj
        notification.handler = self
        self.db.append(kwargs)
        return notification

    def clear(self):
        """Clear all notifications."""
        while self.db:
            del self.db[0]


class Notification(object):

    """A class to represent a notification."""

    def __init__(self, title, screen, app, folder="app", content="", timestamp=None, db=None):
        self.title = title
        self.screen = screen
        self.app = app
        self.folder = folder
        self.content = content
        self.timestamp = timestamp
        self.db = db
        self.obj = None
        self.handler = None

    @property
    def ago(self):
        """Return the time since the notification was created."""
        if self.timestamp is None:
            return "now"

        gtime = gametime.gametime(absolute=True)
        seconds = gtime - self.timestamp
        if seconds < 5:
            return "a few seconds ago"

        ago = time_format(seconds, 4)
        return "{} ago".format(ago)

    def address(self, user):
        """Addresses the notification."""
        if self.obj:
            types = self.obj.types.can("use")
            if types:
                types[0].use(user, self.screen, self.app, self.folder, self.db)
                self.handler.clear()
