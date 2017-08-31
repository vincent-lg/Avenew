"""Module containing the representation of the Room class."""

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
        room = self.room
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

    def set_x(self, caller, x):
        """Set the X value."""
        try:
            x = int(x)
        except ValueError:
            caller.msg("{} isn't a valid integer.".format(x))
            return False
        else:
            self._set_coordinate(caller, "x", x)

    def set_y(self, caller, y):
        """Set the Y value."""
        try:
            y = int(y)
        except ValueError:
            caller.msg("{} isn't a valid integer.".format(y))
            return False
        else:
            self._set_coordinate(caller, "y", y)

    def set_z(self, caller, z):
        """Set the Z value."""
        try:
            z = int(z)
        except ValueError:
            caller.msg("{} isn't a valid integer.".format(z))
            return False
        else:
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
