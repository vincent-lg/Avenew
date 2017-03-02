"""Module containing the Options parameter class."""

import argparse
import shlex

from commands.smart.parameters.base import Parameter

class Options(Parameter):

    """Parse a str into a Linux-like option line.

    The 'argparse' module is used to explicitly extract the
    sting.  It can be easily customized, as the parser is an object
    attribute and can be extended easily enough.  If the options
    cannot be interpreted, a ValueError exception is raised.

    """

    key = "options"

    def __init__(self):
        def n_exit(code=None, msg=None):
            if msg:
                raise ValueError(msg)

        super(Options, self).__init__()
        self.parser = argparse.ArgumentParser(conflict_handler='resolve')
        self.parser.exit = n_exit

    def parse(self, command, args):
        """Parse the specified arguments."""
        args = self.parser.parse_args(shlex.split(args))
        setattr(command, self.attribute, args)
        return ""
