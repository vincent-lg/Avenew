"""
Module containing abstract classes for applications.
"""

from textwrap import dedent

from evennia import Command
from evennia.utils.evform import EvForm
from evennia.utils.utils import class_from_module, lazy_property

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

    def __init__(self, obj, user, type, app=None):
        self.obj = obj
        self.user = user
        self.type = type
        self.app = app
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

    def _add_commands(self):
        """Add the commands in the user CmdSet, if exist."""
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
        )

        # Save the screen in the users' CmdSet
        if self.user and self.user.cmdset.has("computer"):
            for cmdset in self.user.cmdset.get():
                if cmdset.key == "computer":
                    for cmd in cmdset.commands:
                        cmd.screen = self
                    break

    def display(self):
        """
        Display the screen.

        This method should send a message to `self.user`, which contains
        the object currently using the phone/computer.

        """
        if type(self).message:
            self.user.msg(type(self).message)
        else:
            self.user.msg("This screen has nothing to display.")

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
        if isinstance(screen, basestring):
            screen = class_from_module(screen)
        app = app or self.app
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
        new_screen = self.move_to(screen, app, db=db)
        path = type(new_screen).__module__ + "." + type(new_screen).__name__
        db = self.type.db
        if "screen_tree"  not in db:
            db["screen_tree"] = []
        tree = db["screen_tree"]
        app = new_screen.app
        folder = app and type(app).folder or None
        app = app and type(app).app_name or None
        tree.append((path, app, folder, dict(self.db)))

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

    def display(self):
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
        self.user.msg(string)

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

