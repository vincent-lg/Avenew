# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

"""
Room

Rooms are simple containers that has no location of their own.

"""

from collections import defaultdict
from math import sqrt
import re
from textwrap import wrap

from evennia.contrib.ingame_python.typeclasses import EventRoom
from evennia.contrib.ingame_python.utils import register_events
from evennia.utils.utils import lazy_property, list_to_string

from typeclasses.shared import AvenewObject, SharedAttributeHandler

# Constants
RE_KEYWORD = re.compile(r"\B\$\w+")

DESCRIBE = """
Before the room description is displayed.
This event is called on the room before it displays its description to
a character looking at it.  This is a good moment to add dynamism to
descriptions.  To do so, specify a keyword starting with a $ sign in
the text description.  In this event, you will then need to create a
variable with the same name, containing the text to be displayed.
For instance, if you have in your description:
    The terrain slopes $slope.
In the descrive event, you could have something like:
    slope = "east"
The final description will display:
    The terrains slopes east.
Obviously, using conditions in this event allows for more flexibility.

Variables you can use in this event:
    room: the room connected to this event.
    character: the character looking at the description.
"""

@register_events
class Room(AvenewObject, EventRoom):

    """
    A room with coords.

    Rooms are geographic objects with coordinates (X, Y, and Z) that
    are stored as tags.  This allows for a very quick search in the
    database, and simplify the task when retrieving a room at a given
    position, or looking for rooms around a given position.

    """

    _events = {
        "describe": (["room", "character"], DESCRIBE),
    }
    repr = "representations.room.RoomRepr"
    building_menu = "menu.building.room.RoomBuildingMenu"

    @classmethod
    def get_room_at(cls, x, y, z):
        """
        Return the room at the given location or None if not found.

        Args:
            x (int): the X coord.
            y (int): the Y coord.
            z (int): the Z coord.

        Return:
            The room at this location (Room) or None if not found.

        """
        rooms = cls.objects.filter(
                db_tags__db_key=str(x), db_tags__db_category="coordx").filter(
                db_tags__db_key=str(y), db_tags__db_category="coordy").filter(
                db_tags__db_key=str(z), db_tags__db_category="coordz")
        if rooms:
            return rooms[0]

        return None

    @classmethod
    def get_room_with_ident(cls, ident):
        """
        Return the room with the given identifier or None if not found.

        Args:
            ident (str): the room identifier.

        Return:
            The room with this identifier (Room) or None if not found.

        """
        rooms = cls.objects.get_by_attribute(key="ident", value=ident)
        if rooms:
            return rooms[0]

        return None

    @classmethod
    def get_rooms_around(cls, x, y, z, distance):
        """Return the list of rooms around the given coords.

        This method returns a list of tuples (distance, room) that
        can easily be browsed.  This list is sorted by distance (the
        closest room to the specified position is always at the top
        of the list).

        Args:
            x (int): the X coord.
            y (int): the Y coord.
            z (int): the Z coord.
            distance (int): the maximum distance to the specified position.

        Returns:
            A list of tuples containing the distance to the specified
            position and the room at this distance.  Several rooms
            can be at equal distance from the position.

        """
        # Performs a quick search to only get rooms in a kind of rectangle
        x_r = list(reversed([str(x - i) for i in range(0, distance + 1)]))
        x_r += [str(x + i) for i in range(1, distance + 1)]
        y_r = list(reversed([str(y - i) for i in range(0, distance + 1)]))
        y_r += [str(y + i) for i in range(1, distance + 1)]
        z_r = list(reversed([str(z - i) for i in range(0, distance + 1)]))
        z_r += [str(z + i) for i in range(1, distance + 1)]
        wide = cls.objects.filter(
                db_tags__db_key__in=x_r, db_tags__db_category="coordx").filter(
                db_tags__db_key__in=y_r, db_tags__db_category="coordy").filter(
                db_tags__db_key__in=z_r, db_tags__db_category="coordz")

        # We now need to filter down this list to find out whether
        # these rooms are really close enough, and at what distance
        rooms = []
        for room in wide:
            x2 = int(room.tags.get(category="coordx"))
            y2 = int(room.tags.get(category="coordy"))
            z2 = int(room.tags.get(category="coordz"))
            distance_to_room = sqrt(
                    (x2 - x) ** 2 + (y2 - y) ** 2 + (z2 - z) ** 2)
            if distance_to_room <= distance:
                rooms.append((distance_to_room, room))

        # Finally sort the rooms by distance
        rooms.sort(key=lambda tup: tup[0])
        return rooms

    @lazy_property
    def attributes(self):
        return SharedAttributeHandler(self)

    @property
    def x(self):
        """Return the X coordinate or None."""
        x = self.tags.get(category="coordx")
        return int(x) if isinstance(x, str) else None

    @x.setter
    def x(self, x):
        """Change the X coordinate."""
        old = self.tags.get(category="coordx")
        if old is not None:
            self.tags.remove(old, category="coordx")
        if x is not None:
            self.tags.add(str(x), category="coordx")

    @property
    def y(self):
        """Return the Y coordinate or None."""
        y = self.tags.get(category="coordy")
        return int(y) if isinstance(y, str) else None

    @y.setter
    def y(self, y):
        """Change the Y coordinate."""
        old = self.tags.get(category="coordy")
        if old is not None:
            self.tags.remove(old, category="coordy")
        if y is not None:
            self.tags.add(str(y), category="coordy")

    @property
    def z(self):
        """Return the Z coordinate or None."""
        z = self.tags.get(category="coordz")
        return int(z) if isinstance(z, str) else None

    @z.setter
    def z(self, z):
        """Change the Z coordinate."""
        old = self.tags.get(category="coordz")
        if old is not None:
            self.tags.remove(old, category="coordz")
        if z is not None:
            self.tags.add(str(z), category="coordz")

    @property
    def ident(self):
        """Return the room identifier."""
        return self.db.ident

    @ident.setter
    def ident(self, ident):
        """Change the room ident."""
        old = self.db.ident
        self.db.ident = None

        # Check that no other room has this identifier
        if self.get_room_with_ident(ident):
            self.db.ident = old
            raise ValueError("the specified ident {} is being used by another room".format(repr(ident)))

        self.db.ident = ident

    @property
    def prototype(self):
        """Return the room prototyype or None."""
        return self.db.prototype

    @prototype.setter
    def prototype(self, prototype):
        """Change the room prototype."""
        if self.db.prototype:
            self.db.prototype.remove_room(self)

        if prototype:
            prototype.add_room(self)
        self.db.prototype = prototype

    def return_appearance(self, looker):
        """
        This formats a description. It is the hook a 'look' command
        should call.

        Args:
            looker (Object): Object doing the looking.

        """
        if not looker:
            return

        # Get and identify all objects
        visible = (con for con in self.contents if con != looker and
                                                    con.access(looker, "view"))

        exits, users, things = [], [], defaultdict(list)
        for con in visible:
            key = con.get_display_name(looker)
            if con.destination:
                exits.append(key)
            elif con.has_account:
                users.append("|c%s|n" % key)
            else:
                things[key].append(con)

        # Get description, build string
        string = "|c%s|n" % self.get_display_name(looker)
        desc = self.db.desc
        if desc:
            # Format the string
            description = desc

            # Process through the description keywords ($example)
            vars = {}
            if self.db.prototype:
                if self.db.prototype.db.desc:
                    vars["parent"] = self.db.prototype.db.desc

            self.callbacks.call("describe", self, looker)
            match = RE_KEYWORD.search(description)
            while match:
                keyword = match.group()[1:]
                if keyword in vars:
                    var = vars[keyword]
                else:
                    var = self.callbacks.get_variable(keyword)

                start, end = match.span()
                description = description[:start] + var + description[end:]
                match = RE_KEYWORD.search(description)

            # Wrap the description
            final = ""
            for line in description.splitlines():
                if len(line) >= 75:
                    line = "\n".join(wrap("   " + line, 75))
                final += "\n" + line
            description = final
        else:
            description = ""

        string += description

        if exits:
            string += "\n|wExits:|n " + ", ".join(exits)
        if users or things:
            # handle pluralization of things (never pluralize users)
            thing_strings = []
            for key, itemlist in sorted(things.iteritems()):
                nitem = len(itemlist)
                if nitem == 1:
                    key, _ = itemlist[0].get_numbered_name(nitem, looker, key=key)
                else:
                    key = itemlist[0].get_numbered_name(nitem, looker, key=key)[1]
                thing_strings.append(key)
            string += "\n|wYou see:|n " + list_to_string(users + thing_strings)

        return string

    def add_address(self, number, name):
        """
        Add the specified address(es) to this room.

        Args:
            number (int or tuple): number(s) to be connected to this road.
            name (str): the name of the road to be connected to.

        Example:
            room.add_address(3, "first street")
            room.add_address((4, 6), "colony street")

        """
        name = name.lower()
        numbers = (number, ) if isinstance(number, int) else number
        if not self.tags.get(name, category="road"):
            self.tags.add(name, category="road")

        # Add the individual numbers
        if self.db.addresses is None:
            self.db.addresses = {}
        if name not in self.db.addresses:
            self.db.addresses[name] = {}
        addresses = self.db.addresses[name]
        for n in numbers:
            tag = "{} {}".format(n, name)
            if not self.tags.get(name, category="address"):
                self.tags.add(tag, category="address")
            if n not in addresses:
                addresses[n] = ""

    def del_address(self, number, name):
        """
        Remove the address and specific tags.

        Args:
            number (int or tuple): the numbers to be removed.
            name (str): the name of the road to be removed.

        Note:
            This method doesn't remove a road, it just disconnects
            this room from the road name and number.  Meaning that it
            will be inaccessible from the road complex, and the road
            complex will be inaccessible from this road as well.

        """
        name = name.lower()
        numbers = (number, ) if isinstance(number, int) else number
        if self.tags.get(name, category="road"):
            self.tags.remove(name, category="road")

        # Remove the individual numbers
        addresses = self.attributes.get("addresses", {}).get(name, {})
        for n in numbers:
            tag = "{} {}".format(n, name)
            if self.tags.get(name, category="address"):
                self.tags.remove(tag, category="address")
            if n in addresses:
                del addresses[n]


class VehicleRoom(Room):

    """A custom room to fit in vehicle."""

    def return_appearance(self, looker):
        """
        This formats a description. It is the hook a 'look' command
        should call.

        Args:
            looker (Object): Object doing the looking.

        """
        string = Room.return_appearance(self, looker)
        if string is not None:
            string += "\n" + self.location.control_panel(looker)

        return string
