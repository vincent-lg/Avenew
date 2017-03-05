"""Module containing the Direction parameter class."""

from collections import namedtuple

from commands.smart.parameters.base import Parameter
from logic.geo import NAME_DIRECTIONS, NAME_OPP_DIRECTIONS, OPP_DIRECTIONS

# Fake class
Dir = namedtuple("Direction", ("name", "indice", "opp_name", "opp_indice"))

class Direction(Parameter):

    """Parse a direction with aliases (east or e)."""

    key = "direction"

    def __init__(self):
        super(Direction, self).__init__()

        # Error messages
        self.error_invalid = "Sorry, {entry} isn't a valid direction."
        self.error_empty = "You should enter a direction name or alias."

    def parse(self, command, args):
        """Parse the specified arguments."""
        name, sep, remaining = args.partition(" ")
        name = name.lower()
        if not name:
            error = self.error_empty.format(entry=args)
            raise ValueError(error)
        elif name not in NAME_DIRECTIONS:
            error = self.error_invalid.format(entry=args)
            raise ValueError(error)
        else:
            indice = NAME_DIRECTIONS[name]
            name = NAME_OPP_DIRECTIONS[indice]
            opp_indice = OPP_DIRECTIONS[indice]
            opp_name = NAME_OPP_DIRECTIONS[opp_indice]
            setattr(command, self.attribute, Dir(
                    name=name, indice=indice, opp_name=opp_name,
                    opp_indice=opp_indice))

        return remaining
