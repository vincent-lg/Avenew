"""
Text application."""

from auto.apps.base import BaseApp, BaseScreen, AppCommand

class CmdNew(AppCommand):

    """
    Compose a new text message.
    """
    
    key = "add"
    aliases = []
    locks = "cmd:all()"

    def func(self):
        self.msg("That was a new message, congratulations!")


class MainScreen(BaseScreen):

    """Main screen of the text app."""

    commands = [CmdNew]
    
    def display(self):
        """Display the app."""
        self.user.msg("You are in the text app... hurray!")


class TextApp(BaseApp):

    """Text applicaiton.

    """

    app_name = "text"
    start_screen = MainScreen

