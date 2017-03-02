"""Module containing the Number parameter class."""

import re

from commands.smart.parameters.base import Parameter

# Constants
RE_NUMBER = re.compile(r"^\s*(-?\d+)(\s|$)")

class Number(Parameter):

    """Parse a number in an optional range."""

    key = "number"

    def __init__(self):
        super(Number, self).__init__()
        self.min = None
        self.max = None

        # Error messages
        self.error_invalid = "Sorry, {entry} isn't a valid number."
        self.error_empty = "You should enter a number."
        self.error_range = "You should enter a number between {min} and {max}."

    def parse(self, command, args):
        """Parse the specified arguments."""
        expression = RE_NUMBER.search(args)
        if expression:
            number = int(expression.group(1))
            remaining = args[expression.end():]

            # Check the minimum and maximum
            if self.min is not None and number < self.min:
                error = self.error_range.format(min=self.min, max=self.max,
                        number=number)
                raise ValueError(error)

            if self.max is not None and number > self.max:
                error = self.error_range.format(min=self.min, max=self.max,
                        number=number)
                raise ValueError(error)
        elif args.strip():
            error = self.error_invalid.format(entry=args, min=self.min,
                    max=self.max)
            raise ValueError(error)
        elif self.default is not None:
            number = self.default
            remaining = args
        else:
            error = self.error_empty.format(entry=self.args, min=self.min,
                    max=self.max)
            raise ValueError(error)

        # We write the number in the command and return the remaining args
        setattr(command, self.attribute, number)
        return remaining
