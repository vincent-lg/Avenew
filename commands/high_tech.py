# -*- coding: utf-8 -*-

"""
High-tech command set and commands.
"""

from textwrap import dedent

from evennia import CmdSet
from evennia.commands.cmdhandler import CMD_NOINPUT, CMD_NOMATCH
from evennia.utils.ansi import strip_ansi
from evennia.utils.utils import class_from_module, delay

from commands.command import Command
from commands.help import CmdHelp
from world.log import main

# Commands
class CmdText(Command):

    """
    Send a text.
    """

    key = "text"
    help_category = "Comms"

    def access(self, srcobj, access_type="cmd", default=False):
        if srcobj.cmdset.has("computer"):
            return False
        return super(CmdText, self).access(srcobj, access_type, default)

    def func(self):
        """Execute the command."""
        self.caller.msg("That was some text here!")
        menu = TestBuildingMenu(self.caller, self.caller.location)
        menu.open()


class HTCmdHelp(CmdHelp):

    """
    Display help in a computer or phone interface.
    """

    def func(self):
        """Execute the command."""
        screen = getattr(self, "screen", None)
        if self.args.strip():
            super(CmdHelp, self).func()
        else:
            if not screen:
                self.msg("|rSorry, the screen in which you are is not clear.  Please report to admin.|n")
                return

            text = screen.short_help
            text += "\n\nCommands you can use here:"
            if screen.commands:
                for cmd in screen.commands:
                    text += "\n  |y" + cmd.key.ljust(15) + "|n" + cmd.__doc__.strip().splitlines()[0]
            text += "\n  |yback|n           Go back to the previous screen."
            text += "\n  |yhelp|n           Get help on the screen or a command in it."
            text += "\n  |yexit|n           Exit the interface."
            text += "\n\n" + dedent(screen.long_help)
            self.msg(text)



class CmdNoInput(Command):

    """No input has been found."""

    key = CMD_NOINPUT
    locks = "cmd:all()"

    def func(self):
        """Redisplay the screen, if any."""
        if getattr(self, "screen", None) is None:
            main.error("The CmdSet doesn't have a screen attribute.")
            self.msg("An error occurred.  Closing the interface...")
            self.caller.cmdset.delete(ComputerCmdSet)
            return

        screen = self.screen
        screen.display()


class CmdNoMatch(Command):

    """No input has been found."""

    key = CMD_NOMATCH
    locks = "cmd:all()"

    def func(self):
        """Redirect most inputs to the screen, if found."""
        raw_string = self.raw_string.rstrip()
        if getattr(self, "screen", None) is None:
            main.error("The CmdSet doesn't have a screen attribute.")
            self.msg("An error occurred.  Closing the interface...")
            self.caller.cmdset.delete(ComputerCmdSet)
            return

        screen = self.screen
        if screen.user is not self.caller:
            main.error("The recorded screen has user {} while the CmdSet has caller {}".format(screen.user, self.caller))
            self.msg("An error occurred.  Closing the interface...")
            self.caller.cmdset.delete(ComputerCmdSet)
            screen.close()
            return

        # Handle "back" and "quit"
        if raw_string.lower() == "back" and screen.can_back:
            # Move one step ahead
            if screen.previous:
                screen.back()
            else:
                self.msg("You cannot go back.")
        elif raw_string.lower() == "exit" and screen.can_quit:
            self.msg("You quit the interface of {}.".format(screen.obj.get_display_name(self.caller)))
            screen.close()
            screen.type.quit()
        else:
            ret = screen.no_match(strip_ansi(raw_string))
            if not ret:
                screen.wrong_input(raw_string)


class ComputerCmdSet(CmdSet):

    """
    Computer command set.

    """

    key = "computer"
    priority = 5

    def at_cmdset_creation(self):
        """Populates the cmdset with commands."""
        # If someone is already using it, restore
        obj = self.cmdsetobj.db._aven_using
        screen = None
        if obj:
            type = obj.types.get("computer")
            type.apps.load(self.cmdsetobj)
            screen, app_name, folder = type.db["current_screen"]
            app = None
            if app_name:
                app = type.apps.get(app_name, folder)

            Screen = class_from_module(screen)
            screen = Screen(obj, self.cmdsetobj, type, app)
            self.screen = screen
            screen._load_commands()
            for cmd in screen.commands:
                cmd = cmd()
                cmd.screen = screen
                self.add(cmd)

        cmds = [CmdNoInput(), CmdNoMatch(), HTCmdHelp()]
        for cmd in cmds:
            if screen:
                cmd.screen = screen
            self.add(cmd)
