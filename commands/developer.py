# -*- coding: utf-8 -*-

"""This file contains the commands for developers."""

import datetime
import os

from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils.logger import tail_log_file
from evennia.utils.utils import time_format

class CmdLog(MuxCommand):

    """
    Tail and watch game log files.

    Usage:
        @log <logfile>

    This command allows to see the end of a log file, or watch it.
    In this latter case, messages sent to the logger will be directly
    sent to you as well.

    """

    key = "@log"
    locks = "cmd:id(1) or perm(Developers)"
    help_category = "System"

    def func(self):
        """Main function for this command."""
        filename = self.args.strip()
        if "." not in filename:
            filename += ".log"

        path = os.path.join("server/logs", filename)
        now = datetime.datetime.now()
        if not os.path.exists(path) or not os.path.isfile(path):
            self.msg("The {} log file doesn't exist.".format(filename))
        else:
            lines = tail_log_file(filename, 0, 20)
            render = []
            for line in lines:
                line = line.decode("utf-8")
                if line.count(" ") >= 2:
                    date, time, message = line.split(" ", 2)
                    try:
                        entry = datetime.datetime.strptime(date + " " + time, "%Y-%m-%d %H:%M:%S,%f")
                    except ValueError:
                        continue
                    else:
                        seconds = round((now - entry).total_seconds())
                        format = time_format(seconds, 1)
                        render.append("{:>4}: {}".format(format, message))

            if render:
                self.msg("\n".join(render))
            else:
                self.msg("|rNo message could be found in this log file.|n")
