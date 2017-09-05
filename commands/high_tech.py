"""
High-tech command set and commands.
"""

from evennia import CmdSet
from evennia.commands.cmdhandler import CMD_NOMATCH

from commands.command import Command
from world.log import main

# Commands
class CmdText(Command):

    """
    Send a text.
    """

    key = "text"
    help_category = "Comms"

    def access(self, srcobj, access_type="cmd", default=False):
        print "checking access", srcobj
        if srcobj.cmdset.has("computer"):
            print "Computer, return False"
            return False
        return super(CmdText, self).access(srcobj, access_type, default)

    def func(self):
        """Execute the command."""
        self.caller.msg("That was some text here!")
        self.caller.cmdset.add("commands.high_tech.ComputerCmdSet", permanent=True)


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
            ret = screen.no_match(raw_string)
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
        self.add(CmdNoMatch())

