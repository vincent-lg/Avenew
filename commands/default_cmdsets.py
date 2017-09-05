"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""

from evennia import default_cmds
from evennia.commands.default import comms
from evennia.contrib.ingame_python.commands import CmdCallback

from commands.building import CmdEdit, CmdNew
from commands.comms import CmdConnect, CmdDisconnect, CmdChannel
from commands.driving import CmdDrive
from commands.help import CmdHelp
from commands.moving import CmdEnter, CmdLeave
from commands.objects import CmdUse
from commands.road import CmdStartRoad

class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.
    """
    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super(CharacterCmdSet, self).at_cmdset_creation()
        self.add(CmdCallback())
        self.add(CmdEnter())
        self.add(CmdDrive())
        self.add(CmdEdit())
        self.add(CmdNew())
        self.add(CmdHelp())
        self.add(CmdLeave())
        self.add(CmdStartRoad())
        self.add(CmdUse())

        # Channel commands
        self.add(CmdChannel())
        self.add(CmdConnect())
        self.add(CmdDisconnect())

class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """
    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super(AccountCmdSet, self).at_cmdset_creation()
        # Remove all the default channel commands
        self.remove(comms.CmdChannelCreate())
        self.remove(comms.CmdCBoot())
        self.remove(comms.CmdCdesc())
        self.remove(comms.CmdCdestroy())
        self.remove(comms.CmdCemit())
        self.remove(comms.CmdClock())
        self.remove(comms.CmdCWho())
        self.remove(comms.CmdAddCom())
        self.remove(comms.CmdAllCom())
        self.remove(comms.CmdDelCom())
        self.remove(comms.CmdChannels())


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """
    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super(UnloggedinCmdSet, self).at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """
    key = "DefaultSession"

    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As and example we just add the empty base `Command` object.
        It prints some info.
        """
        super(SessionCmdSet, self).at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
