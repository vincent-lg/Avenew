"""
Tests for SmartCommands.
"""

from evennia.commands.default.tests import CommandTest

from commands.smart.command import SmartCommand

class CmdRoll(SmartCommand):

    """
    Roll a dice.

    Usage:
        roll [nmber]

    Roll a dice several times.

    """

    def setup(self):
        """Setup the command's arguments."""
        number = self.params.add("number", default=1)
        number.min = 1
        number.max = 6

    def execute(self):
        """Execute the command."""
        number = self.number
        if number == 1:
            msg = "You roll a dice once."
        elif number == 2:
            msg = "You roll a dice twice."
        else:
            msg = "You roll a dice {} times.".format(number)
        self.caller.msg(msg)


class CmdAddroom(SmartCommand):

    """
    Add a room.

    Usage:
        addroom [options]

    Available options:
        -d (--desc): Copy the description in the new room.
        -e (--exits): create logical exits in both directions.

    """

    def setup(self):
        """Setup the command's arguments."""
        parser = self.params.add("options").parser
        parser.prog = "Addroom"
        parser.add_argument("-d", "--desc", action="store_true")
        parser.add_argument("-e", "--exits", action="store_true")
        parser.add_argument("-i", type=int)

    def execute(self):
        """Execute the command."""
        desc = self.options.desc
        exits = self.options.exits
        msg = ", ".join([name + "=" + ("yes" if value else "no") for \
                name, value in sorted(dict(desc=desc, exits=exits).items())])
        if self.options.i:
            msg += ", i=" + str(self.options.i)

        self.msg(msg)


# Tests
class TestSmart(CommandTest):
    "tests the look command by simple call"
    def test_single_default(self):
        """Test a SmartCommand with one optional parameter."""
        self.call(CmdRoll(), "", "You roll a dice once.")

    def test_single(self):
        """Test a SmartCommand with one provided parameter."""
        self.call(CmdRoll(), "1", "You roll a dice once.")
        self.call(CmdRoll(), "2", "You roll a dice twice.")
        self.call(CmdRoll(), "5", "You roll a dice 5 times.")

    def test_single_errors(self):
        """Test a SmartCommand with wrong parameters."""
        self.call(CmdRoll(), "no", "Sorry, no isn't a valid number.")
        self.call(CmdRoll(), "8",
                "You should enter a number between 1 and 6.")
        self.call(CmdRoll(), "-3",
                "You should enter a number between 1 and 6.")

    def test_options(self):
        """Test a command with options."""
        self.call(CmdAddroom(), "-d", "desc=yes, exits=no")
        self.call(CmdAddroom(), "-ed", "desc=yes, exits=yes")
        self.call(CmdAddroom(), "--exits", "desc=no, exits=yes")
        self.call(CmdAddroom(), "-i 3", "desc=no, exits=no, i=3")
        self.call(CmdAddroom(), "-i",
                "Addroom: error: argument i: expected one argument")
