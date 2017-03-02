"""
Edit Command set

"""

from textwrap import dedent, wrap

from evennia.commands import cmdhandler
from evennia import Command as BaseCommand
from evennia.commands.cmdset import CmdSet

class EditCmdSet(CmdSet):

    key = "Editing"
    mergetype = "Replace"
    priority = 102

    def at_cmdset_creation(self):
        self.add(EditCommand)

_CMD_NOMATCH = cmdhandler.CMD_NOMATCH
_CMD_NOINPUT = cmdhandler.CMD_NOINPUT

class EditCommand(BaseCommand):

    key = _CMD_NOMATCH
    aliases = _CMD_NOINPUT
    locks = "cmd:all()"
    opt_symbol = "/"
    options = {
            "d": "delete_lines",
             "q": "quit",
   }

    def get_description(self):
        """Return the string attribute of the edited object."""
        if self.caller.db.editing is None:
            self.caller.msg("|rAn error occurre, no editing information.|n")
            self.quit()
            return

        object = self.caller.db.editing["object"]
        attr = self.caller.db.editing["attr"]
        description = getattr(object.db, attr)
        return description

    def display_desc(self, caller=None, description=None):
        """Display the desc to the caller of the command."""
        if caller is None:
            caller = self.caller

        if description is None:
            description = self.get_description()

        lines = []
        i = 1
        for line in description.splitlines():
            if len(line) > 75:
                line = str(i).rjust(2) + " " + "\n   ".join(wrap(
                        line, 75))
            else:
                line = str(i).rjust(2) + " " + line
            line = line.replace("|", "||")
            lines.append(line)
            i += 1

        if not lines:
            lines.append("|bEmpty description.|n")

        msg = dedent("""
            Editor:

            Commands:
             |yEnter a simple line of text to add it as a new paragraph|n.
             |y{opt}d *|n to delete every line in the description.
             |y{opt}d <number>|n to delete a line in the description.
             |y{opt}q|n to quit the editor.

            {description}
            """.strip("\n")).format(
                    opt=type(self).opt_symbol,
                    description="\n".join(lines))

        caller.msg(msg)

    def update_desc(self, new_description):
        """Update the description and save it directly."""
        object = self.caller.db.editing["object"]
        attr = self.caller.db.editing["attr"]
        setattr(object.db, attr, new_description)

    def func(self):
        """Main bulk of the command."""
        text = self.get_description()
        msg = self.raw_string.strip("\n")

        # If 'msg' begins with an option symbol
        if msg.startswith(type(self).opt_symbol):
            msg = msg[1:]
            option, sep, arguments = msg.partition(" ")
            option = option.lower()

            # Try to find the method linked with this option
            method_name = type(self).options.get(option)
            if method_name:
                getattr(self, method_name)(arguments)
            else:
                self.caller.msg("|rUnknown option ({}).|n".format(option))
        else:
            # Add the text to the description
            if text is None:
                text = ""

            if text:
                text += "\n"

            text += msg
            self.update_desc(text)
            self.display_desc()

    def delete_lines(self, arguments):
        """Delete one or several lines.

        Syntax:
            {opt}d *
            {opt}d <line number>
            {opt}d <from>-<to>

        """
        description = self.get_description()
        lines = description.splitlines()
        arguments = arguments.strip()
        if arguments == "*":
            self.update_desc("")
            self.display_desc()
        elif arguments.isdigit():
            number = int(arguments)

            try:
                assert number > 0
                line = lines[number - 1]
            except (AssertionError, IndexError):
                self.caller.msg("|rWrong line number: {}.|n".format(number))
            else:
                del lines[number - 1]
                self.update_desc("\n".join(lines))
                self.display_desc()
        else:
            self.caller.msg("|rInvalid syntax for {}d.|n".format(
                    type(self).opt_symbol))

    def quit(self, arguments):
        """Quit the editor.

        Syntax:
            {opt}q

        """
        self.caller.msg("Closing the editor.")
        self.caller.cmdset.delete()
