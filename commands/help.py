# -*- coding: utf-8 -*-

"""
The help command. The basic idea is that help texts for commands
are best written by those that write the commands - the admins. So
command-help is all auto-loaded and searched from the current command
set. The normal, database-tied help system is used for collaborative
creation of other help topics such as RP help or game-world aides.
"""

from django.conf import settings
from evennia.commands.default.help import CmdHelp as OldCmdHelp
from evennia.utils.utils import dedent, fill

## Constants
_DEFAULT_WIDTH = settings.CLIENT_DEFAULT_WIDTH
_SEP = "|C" + "-" * _DEFAULT_WIDTH + "|n"

class CmdHelp(OldCmdHelp):

    key = "help"
    suggestion_maxnum = 0

    @staticmethod
    def format_help_entry(title, help_text, aliases=None, suggested=None):
        """
        This visually formats the help entry.
        This method can be overriden to customize the way a help
        entry is displayed.

        Args:
            title (str): the title of the help entry.
            help_text (str): the text of the help entry.
            aliases (list of str or None): the list of aliases.
            suggested (list of str or None): suggested reading.

        Returns the formatted string, ready to be sent.

        """
        string = _SEP + "\n"
        if title:
            string += "|CAide sur |y%s|n" % title
        if aliases:
            string += " |C(alias : %s|C)|n" % ("|C,|n ".join("|y%s|n" % ali for ali in aliases))
        if help_text:
            string += "\n%s" % dedent(help_text.rstrip())
        string.strip()
        string += "\n" + _SEP
        return string

    @staticmethod
    def format_help_list(hdict_cmds, hdict_db):
        """
        Output a category-ordered list. The input are the
        pre-loaded help files for commands and database-helpfiles
        respectively.  You can override this method to return a
        custom display of the list of commands and topics.
        """
        string = ""
        if hdict_cmds and any(hdict_cmds.values()):
            string += "\n" + _SEP + "\n   |CAide sur les commandes|n\n" + _SEP
            for category in sorted(hdict_cmds.keys()):
                string += "\n  |w%s|n:\n" % (str(category).title())
                string += "|G" + fill("|C, |G".join(sorted(hdict_cmds[category]))) + "|n"
        if hdict_db and any(hdict_db.values()):
            string += "\n\n" + _SEP + "\n\r  |CAutres fichiers d'aide|n\n" + _SEP
            topics = []
            for category in hdict_db.keys():
                topics += hdict_db[category]
            print repr(topics)
            topics.sort()
            string += "\n  |G" + fill(", ".join([str(topic) for topic in topics])) + "|n"

        return string

    def should_list_cmd(self, cmd, caller):
        """Commands with spaces aren't shown."""
        return " " not in cmd.key
