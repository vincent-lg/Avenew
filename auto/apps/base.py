"""
Module containing abstract classes for applications.
"""

from textwrap import dedent, wrap

from evennia import Command
from evennia.utils.evform import EvForm
from evennia.utils.utils import class_from_module, inherits_from, lazy_property

class BaseApp(object):

    """
    Abstract class for all applications.

    All applications should contain a class inheriting from `BaseApp`.

    """

    app_name = "" # Application name
    folder = "app"
    start_screen = None

    def __init__(self, obj, user, type):
        self.obj = obj
        self.user = user
        self.type = type

    def __repr__(self):
        return "<App {} ({} folder)>".format(type(self).app_name, type(self).folder)

    @lazy_property
    def db(self):
        """Return an application-specific storage as a dict."""
        type_db = self.type.db
        if "app_storage" not in type_db:
            type_db["app_storage"] = {}
        storage = type_db["app_storage"]
        if type(self).folder not in storage:
            storage[type(self).folder] = {}
        storage = storage[type(self).folder]
        if self.app_name not in storage:
            storage[type(self).app_name] = {}
        return storage[self.app_name]

    @classmethod
    def notify(cls, obj, title, message="", content="", screen=None, db=None):
        """Send a message to the owner of the app if needed.

        This method is called when a notificaiton has to be sent.
        It can do 3 things, depending on context:

        1. Send the message to the object location (room).
        2. Alert the user of the object (if one).
        3. Create a notification for the object (if no one is using it).

        Args:
            obj (Object): the object being notified.
            title (str): the title of the notification to be displayed.
            content (str): the content of the notification (can be an empty string).
            message (str, optional): the message to be displayed by the location.
            screen (str or Screen, optional): the screen's path (default to the app's start screen).
            db (dict, optional): the optional arguments to give to the screen.

        Note:
            Notifications are defined in the app because it might be
            useful to override this method.  However, the common use
            case is to write a static method on the screen itself that calls
            the application's `notify` method.  The reason for doing it
            this way is, a screen usually has only one notification process,
            but it can easily change message this way, so it doesn't need as
            many arguments.  See other applications for examples.

        """
        screen = screen or cls.start_screen
        if isinstance(screen, basestring):
            if "." not in screen:
                screen = cls.__module__ + "." + screen
        else:
            screen = type(screen).__module__ + "." + type(screen).__name__
        app = cls.app_name
        folder = cls.folder
        types = obj.types.has("notifications")
        type = types and types[0] or None

        # Try to locate the room
        location = obj.location
        while not inherits_from(location, "typeclasses.rooms.Room"):
            if location is None:
                break

            location = location.location

        # If a room has been found and a message is to be sent
        user = type and type.db.get("used", None) or None
        if message and location:
            location.msg_contents(message, exclude=[user], mapping=dict(obj=obj))

        # Send to the user, if any
        if user and user.has_account:
            to_send = title + ": " + content
            to_send = "\n    ".join(wrap(to_send, 74))
            user.msg(to_send)
        else:
            # If no current user, add a notification
            type.notifications.add(title, screen, app, folder, content=content, db=db)


class BaseScreen(object):

    """Abstract class for a screen.

    A screen represents the active context for the one using the phone
    or computer.  A screen can be as simple as a question, asking
    between "yes" and "no".  A screen can also be much more complex,
    with multiple commands.

    A screen has several commands.  You should place them in the
    `commands` class variable of the screen.  An application usually
    has several screens.

    Being responsible for displaying information, the screen can provide different class variables:
        - `message` should contain the text to be displayed.
        - Otherwise, you can simply override the `display` method to
                display something a bit more customized.  You might
                be interested in checking the `display_form` method
                that allows to display an EvForm, particvularly useful
                for a screen.

    """

    message = None
    commands = []
    can_back = True # Can go back in the screen tree
    can_quit = True # Can quit the screen and close the interface
    back_screen = None
    show_header = True

    def __init__(self, obj, user, type, app=None, add_commands=True):
        self.obj = obj
        self.user = user
        self.type = type
        self.app = app

        if add_commands:
            self._add_commands()

    @lazy_property
    def db(self):
        """Return the screen-specific storage."""
        db = self.type.db
        if "screen_storage" not in db:
            db["screen_storage"] = {}
        return db["screen_storage"]

    @property
    def previous(self):
        """Return the previous screen in the screen tree or None."""
        db = self.type.db
        tree = list(db.get("screen_tree", {}))
        path = type(self).__module__ + "." + type(self).__name__
        if tree and tree[-1][0] == path:
            del tree[-1]

        app_name = folder = None
        if self.app:
            app_name = type(self.app).app_name
            folder = type(self.app).folder

        back_screen = [type(self).back_screen, app_name, folder, None]
        return tree and tree[-1] or back_screen

    def _load_commands(self):
        """Load the required commands."""
        for i, cmd in enumerate(type(self).commands):
            if isinstance(cmd, basestring):
                if "." not in cmd:
                    cmd = type(self).__module__ + "." + cmd
                type(self).commands[i] = class_from_module(cmd)

    def _add_commands(self):
        """Add the commands in the user CmdSet, if exist."""
        self._load_commands()
        # Add to the CmdSet
        if self.user and self.user.cmdset.has("computer"):
            for cmdset in self.user.cmdset.get():
                if cmdset.key == "computer":
                    for cmd in type(self).commands:

                        cmdset.add(cmd())
                    self.user.cmdset.remove(cmdset)
                    self.user.cmdset.add(cmdset)
                    break

    def _delete_commands(self):
        """Remvoe this screen's commands."""
        if self.user and self.user.cmdset.has("computer"):
            for cmdset in self.user.cmdset.get():
                if cmdset.key == "computer":
                    for cmd in type(self).commands:
                        cmdset.remove(cmd)
                    break

    def _save(self):
        """Save the current screen."""
        self.type.db["current_screen"] = (
                type(self).__module__ + "." + type(self).__name__,
                self.app and type(self.app).app_name or None,
                self.app and type(self.app).folder or None,
                dict(self.db),
        )

        # Save the screen in the users' CmdSet
        if self.user and self.user.cmdset.has("computer"):
            for cmdset in self.user.cmdset.get():
                if cmdset.key == "computer":
                    cmdset.screen = self
                    for cmd in cmdset.commands:
                        cmd.screen = self
                    break

    def format_cmd(self, text, key=None):
        """Format the command as a colored, clickable link.

        Args:
            text (str): the text of the command/clickable link.
            key (str, optional): the key of the command to enter
                    (`text` by default).

        """
        key = key or text
        text = text.upper()
        return "|y|lc{key}|lt{text}|le|n".format(key=key, text=text)

    def display(self):
        """
        Display the screen.

        This method should send a message to `self.user`, which contains
        the object currently using the phone/computer.

        Note:
            More often than not, you will not override this method.
            Override `get_text` instead, which should return the text
            to display.  Doing so allows ease of testing the app
            afterward.

        """
        text = self.get_text()
        if text:
            text = dedent(text.strip("\n"))
            if type(self).show_header:
                lines = text.splitlines()
                lines[0] = lines[0] + " ({back} to go back, {exit} to exit, {help} to get help)".format(
                        back=self.format_cmd("back"), exit=self.format_cmd("exit"), help=self.format_cmd("help"))
                text = "\n".join(lines)

            self.user.msg(text)

    def display_form(self, form, *fields):
        """
        Display a form to the user.

        This is particularly useful ti display a realistic screen.
        Forms use the EvForm syntax.  The fields are used to create a
        dictionary of numbers in the provided order.

        Example:
            form = '''
            .--------------------------.
            |       New message        |
            .--------------------------.
              To: x1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
              Attachment: x2xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
              Text:
                   x3xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
                   xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
                   xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
            '''
            self.display_form(form, "600-9917", "(none yet)",
                    "So are you coming tomorrow or not?")

        """
        self.user.msg(self.get_form(form, *fields))

    def get_form(self, form, *fields):
        """Return the EvForm corresponding to a form."""
        cells = {i + 1: field for i, field in enumerate(fields)}
        form = EvForm(cells=cells, form={"CELLCHAR": "x", "TABLECHAR": "c", "FORM": dedent("\n" + form.lstrip("\n"))})
        return form

    def close(self):
        """Close the screen, erasing its storage."""
        db = self.type.db
        if "current_screen" in db:
            del db["current_screen"]
        if "screen_storage" in db:
            del db["screen_storage"]

        if "screen_tree" in db:
            del db["screen_tree"]

    # Move methods
    def back(self):
        """Go back in the screen tree.

        This method forces moving back in the previous screen.  The
        previous screen is either at the end of the screen tree, or
        one step above, depending on whether the current screen is
        in the screen tree.

        Returns:
            new_screen (Screen or None): the new screen in which the user now is.

        """
        previous = self.previous
        app = folder = None
        if previous:
            previous, app, folder, db = previous
            previous = class_from_module(previous)
            self._delete_commands()
            self.db.clear()
            if db:
                self.db.update(db)

            if app and folder:
                app = self.type.apps.get(app, folder)

            previous = previous(self.obj, self.user, self.type, app)
            path = type(self).__module__ + "." + type(self).__name__
            db = self.type.db
            tree = db.get("screen_tree", [])
            if tree and tree[-1][0] == path:
                del tree[-1]
            previous._save()
            previous.display()
            return previous
        return None

    def move_to(self, screen, app=None, folder=None, db=None):
        """
        Move to another screen, not adding it to the screen tree.

        This method is used to change the current screen without putting
        the new one in the screen tree: the screen tree is a list of
        screens that were browsed, and is used to go back.  Some screens
        don't need to be put in the screen tree, like confirmation
        messages, error messages, and other such screens.  Most of
        the time, you will use the `next` method, that does the same
        thing but records the new screen in the screen tree.

        Args:
            screen (Screen class or str): the new screen as a class or
                    path leading to it.
            app (App, optional): the screen app.
            db (dict, optional): a dictionary of data to send to the new screen.

        Note:
            If `app` isn't specified, use the current screen's `app`.

        Returns:
            new_screen (Screen): the new screen object.

        """
        app = app or self.app
        if isinstance(screen, basestring):
            if "." not in screen: # We assume it means a relative import in the current module
                screen = type(app).__module__ + "." + screen

            screen = class_from_module(screen)
        self._delete_commands()
        new_screen = screen(self.obj, self.user, self.type, app)
        new_screen._save()

        # Before displaying the screen, add the optional data
        if db:
            data = new_screen.db
            for key, value in db.items():
                data[key] = value

        new_screen.display()
        return new_screen

    def next(self, screen, app=None, db=None):
        """Go to a new screen and save it in the screen tree.

        This method is used to change the current screen while putting
        the new one in the screen tree: the screen tree is a list of
        screens that were browsed, and is used to go back.  Some screens
        don't need to be put in the screen tree, like confirmation
        messages, error messages, and other such screens.  Most of the
        time though, you will want to record them in the screen tree.
        You can think of the screen as a trail of bread crumbs that
        expands when a user opens an app.

        Args:
            screen (Screen class or str): the new screen as a class or
                    path leading to it.
            app (App, optional): the screen app.
            db (dict, optional): a dictionary of data to send to the new screen.

        Note:
            If `app` isn't specified, use the current screen's `app`.

        Returns:
            new_screen (Screen): the new screen object.

        """
        db = db or {}
        new_screen = self.move_to(screen, app, db=db)
        path = type(new_screen).__module__ + "." + type(new_screen).__name__
        if "screen_tree"  not in self.type.db:
            self.type.db["screen_tree"] = []
        tree = self.type.db["screen_tree"]
        app = new_screen.app
        folder = app and type(app).folder or None
        app = app and type(app).app_name or None
        tree.append((path, app, folder, dict(db)))

    # Input methods
    def no_match(self, string):
        """Something that doesn't match any command has been entered by the user.

        Override this method to handle specific cases of the application.  Try your best to keep things in commands whenever possible, however, this is much cleaner.

        Args:
            string (str): the input string entered by the user.

        Return:
            found (bool): whether this input was processed correctly.
                    If `found` is False, call the screen help.

        """
        return False

    def wrong_input(self, string):
        """The `no_match` method couldn't process the input.

        This method should be overridden to give specific help regarding
        this screen.  The default help will just list the commands
        in the applicaiton-specific category.

        """
        self.user.msg("Wrong input.")


class MainScreen(BaseScreen):

    """Main screen on opening the phone/computer.

    The role of this screen is to display the installed apps on this
    device.  It doesn't create any commands, merely being called when
    no command matches.

    """

    can_back = False # At this point we shouldn't try to get back
    show_header = False

    def get_text(self):
        """Display the installed apps."""
        string = dedent("""
            AvenOS 12.0            [6G]           [Bluetooth]           [96%}
        """.lstrip("\n")) + "\n"
        i = 0
        for app in self.type.apps:
            if i > 0 and i % 3 == 0:
                string += "\n" + " " * 4
            string += "|lc{name}|lt{name:<15}|le".format(name=app.app_name)

        string += "\n\n" + dedent("""
            Enter the first letters to open this app.  Type |hEXIT|n to quit the interface."
        """.lstrip("\n"))
        return string

    def no_match(self, string):
        """A no match has been entered, perhaps an application name."""
        string = string.strip()
        app = self.type.apps.get(string, "app")
        if not app:
            string = string.lower()
            matches = []
            for app in self.type.apps:
                if type(app).folder == "app" and type(app).app_name.lower().startswith(string):
                    matches.append(app)

            # If only one match, just move there
            if len(matches) == 1:
                app = matches[0]
            else:
                names = [type(app).app_name for app in matches]
                names.sort(key=lambda name: name.lower())
                self.msg("Which app do you want to open? {}".format(", ".join(names)))
                return True

        screen = type(app).start_screen
        self.next(screen, app)
        return True


class AppCommand(Command):

    """An applicaiton-specific command."""

    help_category = "Application-specific"

