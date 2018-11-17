# -*- coding: utf-8 -*-

"""
Commands

Commands describe the input the account can do to the game.

"""

from __future__ import absolute_import, unicode_literals
import time

import sys
import evennia
from evennia import ChannelDB
from evennia import Command as BaseCommand
from evennia.commands.default.muxcommand import MuxCommand as BaseMuxCommand

from world.log import command as log

class Command(BaseCommand):
    """
    Inherit from this if you want to create your own command styles
    from scratch.  Note that Evennia's default commands inherits from
    MuxCommand instead.

    Note that the class's `__doc__` string (this text) is
    used by Evennia to create the automatic help entry for
    the command, so make sure to document consistently here.

    Each Command implements the following methods, called
    in this order (only func() is actually required):
        - at_pre_command(): If this returns True, execution is aborted.
        - parse(): Should perform any extra parsing needed on self.args
            and store the result on self.
        - func(): Performs the actual work.
        - at_post_command(): Extra actions, often things done after
            every command, like prompts.

    """

    def at_pre_cmd(self):
        """Before the command is called."""
        self.t1 = time.time()

    def at_post_cmd(self):
        """After the command has executed."""
        t1 = getattr(self, "t1", None)
        key = getattr(self, "key", "unknown")
        if t1:
            t2 = time.time()
            total = int(round((t2 - t1) * 1000))
        else:
            total = "?"

        log.debug("{}MS for {}".format(total, key))


class MuxCommand(BaseMuxCommand):

    # Timed MuxCommands

    def at_pre_cmd(self):
        """Before the command is called."""
        self.t1 = time.time()

    def at_post_cmd(self):
        """After the command has executed."""
        t1 = getattr(self, "t1", None)
        key = getattr(self, "key", "unknown")
        if t1:
            t2 = time.time()
            total = int(round((t2 - t1) * 1000))
        else:
            total = "?"

        log.debug("{}MS for {}".format(total, key))
