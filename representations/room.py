"""Module containing the representation of the Room class."""

from evennia.utils.evtable import EvTable

from representations.base import BaseRepr

FORM = """
.-------------------------------------------------------------------------.
| Name: xxxxxxxxxxxx1xxxxxxxxxxxxxxxxx               X=xx2x Y=xx3x Z=xx4x |
|                                                                         |
| Desc: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx |
|       xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx5xxxxxxxxxxxxxxxxxxxxxxxxxx |
|       xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx |
|       xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx |
|                                                                         |
.-------------------------------------------------------------------------.
"""

class RoomRepr(BaseRepr):

    """The room representation."""

    fields = {
            "x": int,
            "y": int,
            "z": int,
            "key": str,
    }
    to_display = ["name", "x", "y", "z", "desc"]
    form = FORM

    def get_desc(self, caller):
        return self.obj.db.desc

    def _set_coordinate(self, caller, which, value):
        """
        Change a coordinate.

        Args:
            caller (Character, Account or Session): the caller.
            which (str): the coordinate to modify ("x", "y" or "z").
            value (int ot None): the new coordinate.

        """
        room = self.obj
        if which not in ("x", "y", "z"):
            raise ValueError("Invalid coordinate {}.".format(which))

        if getattr(room, which) == value:
            caller.msg("This room already has these coordinates.")
            return False

        elif value is not None:
            coords = [room.x, room.y, room.z]
            if which == "x": coords[0] = value
            elif which == "y": coords[1] = value
            else: coords[2] = value

            other = type(room).get_room_at(*coords)
            if other:
                caller.msg("The room {} already has these coordinates.".format(
                        other.get_display_name(caller)))
                return False

        setattr(room, which, value)
        if value is None:
            caller.msg("Cleared value for {} on {}.".format(
                    which.upper(), room.get_display_name(caller)))
        else:
            caller.msg("New value {} = {} for {}.".format(
                    which.upper(), value, room.get_display_name(caller)))

    def add_address(self, caller, value):
        """Add a new address.

        The value should contain the number, road name, a colon and
        the address name.

        Example:
            3 first street: The public library

        """
        if not value or ":" not in value:
            caller.msg("Enter the number, road name, a colon and the address name.  For instance:")
            caller.msg("@address/add here = 3 first street: The public library")
            return

        address, name = value.split(":", 1)
        if " " not in address:
            caller.msg("Enter the number, road name, a colon and the address name.  For instance:")
            caller.msg("@address/add here = 3 first street: The public library")
            return

        number, address = address.split(" ", 1)
        address = address.lower()
        name = name.strip()

        try:
            number = int(number)
        except ValueError:
            caller.msg("{} is an invalid number.".format(number))
            return

        if address not in self.obj.db.addresses:
            caller.msg("{} cannot be found here.".format(address))
            return

        addresses = self.obj.db.addresses[address]
        if number not in addresses:
            caller.msg("{} isn't present in {} at this location.".format(number, address))
            return

        addresses[number] = name
        caller.msg("Address added: {} {}: {}".format(number, address, name))

    def set_x(self, caller, x):
        """Set the X value."""
        self._set_coordinate(caller, "x", x)

    def set_y(self, caller, y):
        """Set the Y value."""
        self._set_coordinate(caller, "y", y)

    def set_z(self, caller, z):
        """Set the Z value."""
        self._set_coordinate(caller, "z", z)

    def clear_x(self, caller):
        """Clear the X value."""
        self._set_coordinate(caller, "x", None)

    def clear_y(self, caller):
        """Clear the Y value."""
        self._set_coordinate(caller, "y", None)

    def clear_z(self, caller):
        """Clear the Z value."""
        self._set_coordinate(caller, "z", None)

    def display(self, caller):
        """Display the object."""
        form = self.get_form(caller)
        numbers = []
        for road, address in sorted(self.obj.db.addresses.items()):
            for number, name in sorted(address.items()):
                numbers.append("{} {}: {}".format(number, road, name))

        if numbers:
            lines = form.splitlines()
            for number in numbers:
                lines.insert(-1, "|     {:<67} |".format(number))
            lines.insert(-1, "| " + " " * 72 + "|")
        caller.msg("\n".join(lines))
