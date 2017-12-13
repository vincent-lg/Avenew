# -*- coding: utf-8 -*-

"""
The help command. The basic idea is that help texts for commands
are best written by those that write the commands - the admins. So
command-help is all auto-loaded and searched from the current command
set. The normal, database-tied help system is used for collaborative
creation of other help topics such as RP help or game-world aides.
"""

from evennia.commands.default.help import CmdHelp as OldCmdHelp

class CmdHelp(OldCmdHelp):

    key = "help"

    def should_list_cmd(self, cmd, caller):
        """Commands with spaces aren't shown."""
        return " " not in cmd.key
